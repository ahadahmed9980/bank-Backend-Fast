from app.utils.objects import from_Object_id, to_Object_id
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.database.mongodb import users_collection, session_collection
from app.utils.password import hash_Password, compare_password
from app.utils.tokens import (
    create_refresh_token,
    hash_refresh_token,
    creat_access_token,
)


# reg user
async def userRegister(data: dict) -> dict:

    isExist = await users_collection.find_one({"email": data["email"]})

    if isExist:
        raise HTTPException(status_code=409, detail="user already exist please login")

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


# login user
async def userLogin(
    data: dict,
    ip: str | None,
    user_agent: str | None,
) -> dict:
    user = await users_collection.find_one({"email": data["email"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not compare_password(data["password"], user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    # session create
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
    access_token = creat_access_token(user["_id"], session_id)
    refresh_token = create_refresh_token(user["_id"], session_id)
    # save hash in db
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


# get active session
async def getActiveSession(user_id, session_id):
    return await session_collection.find_one(
        {"_id": session_id, "userId": user_id, "revoke": False}
    )


# rotate refresh token
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
