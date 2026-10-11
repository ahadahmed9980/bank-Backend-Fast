import hmac
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import JWT_SECRET, JWT_ALGORITHM
from app.database.mongodb import users_collection, session_collection
from app.utils.objects import from_Object_id
from app.utils.password import hash_Password, compare_password
from app.utils.tokens import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)


# Register user
async def userRegister(data: dict) -> dict:
    isExist = await users_collection.find_one({"email": data["email"]})
    if isExist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user already exist please login",
        )

    document = {
        "name": data["name"],
        "email": data["email"],
        "password": hash_Password(data["password"]),
        "created_at": datetime.now(timezone.utc),
    }

    result = await users_collection.insert_one(document)
    document["_id"] = result.inserted_id
    document.pop("password", None)

    return from_Object_id(document)


# Login user
async def userLogin(
    data: dict,
    ip: str | None,
    user_agent: str | None,
) -> dict:
    user = await users_collection.find_one({"email": data["email"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not compare_password(data["password"], user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create session document
    session_document = {
        "userId": user["_id"],
        "ip": ip,
        "userAgent": user_agent,
        "revoke": False,
        "refreshTokenHash": None,
        "createdAt": datetime.now(timezone.utc),
    }
    session_result = await session_collection.insert_one(session_document)
    session_id = session_result.inserted_id

    access_token = create_access_token(user["_id"], session_id)
    refresh_token = create_refresh_token(user["_id"], session_id)

    # Save initial refresh token hash in session
    await session_collection.update_one(
        {"_id": session_id},
        {"$set": {"refreshTokenHash": hash_refresh_token(refresh_token)}},
    )

    return {
        "status": "success",
        "message": "Login successful",
        "data": {
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name"),
                "email": user["email"],
            },
            "tokens": {
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "tokenType": "bearer",
            },
        },
    }


# Get active session
async def getActiveSession(user_id, session_id):
    return await session_collection.find_one(
        {"_id": session_id, "userId": user_id, "revoke": False}
    )


# Rotate refresh token hash in session collection
async def rotateRefreshToken_hash(user_id, session_id, old_hash, new_hash):
    result = await session_collection.update_one(
        {
            "_id": session_id,
            "userId": user_id,
            "revoke": False,
            "refreshTokenHash": old_hash,
        },
        {
            "$set": {
                "refreshTokenHash": new_hash,
            }
        },
    )
    return result.modified_count == 1


# Rotate refresh token logic
async def userRefreshToken(incoming_token: str) -> dict:
    # 1. Verify and decode incoming token
    try:
        decoded = jwt.decode(
            incoming_token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = ObjectId(decoded["id"])
        session_id = ObjectId(decoded["sessionId"])
    except HTTPException:
        raise
    except (InvalidTokenError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # 2. Check user exists
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # 3. Check session is active
    session = await getActiveSession(user_id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked session",
        )

    # 4. Compare token hash
    incoming_hash = hash_refresh_token(incoming_token)
    stored_hash = session.get("refreshTokenHash")
    if not stored_hash or not hmac.compare_digest(stored_hash, incoming_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token hash",
        )

    # 5. Generate new access token and refresh token
    new_access_token = create_access_token(user_id, session_id)
    new_refresh_token = create_refresh_token(user_id, session_id)
    new_hash = hash_refresh_token(new_refresh_token)

    # 6. Rotate hash in database
    rotated = await rotateRefreshToken_hash(
        user_id,
        session_id,
        stored_hash,
        new_hash,
    )
    if not rotated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token already used",
        )

    return {
        "message": "Access token refreshed successfully",
        "accessToken": new_access_token,
        "refreshToken": new_refresh_token,
    }
