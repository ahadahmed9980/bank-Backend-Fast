from fastapi import (
    APIRouter,
    Body,
    Cookie,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import JWT_SECRET, JWT_ALGORITHM
from app.database.mongodb import users_collection, session_collection


async def get_current_user(request: Request):
    authorization = request.headers.get("Authorization", " ")
    token = None
    if authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    token = token or request.cookies.get("accessToken") or request.cookies.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token is required"
        )
    # now we have to verify jwt
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        user_id = ObjectId(decoded["id"])
        session_id = ObjectId(decoded["sessionId"])
    except (InvalidTokenError, InvalidId, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

        # check user data in db
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    # now find session in db
    session = await session_collection.find_one(
        {"_id": session_id, "userId": user_id, "revoke": False}
    )
    if not session:
        raise HTTPException(status_code=401, detail="session is invalid or revoke")
    request.state.session = session
    return user
