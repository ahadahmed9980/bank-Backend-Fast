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
from app.model.user_model import (
    userRegister,
    userLogin,
    userRefreshToken,
)
from app.schema.user_schema import UserCreate, UserLogin_Schema
from app.schema.auth_schema import RefreshRequest, RefreshResponse

import hmac
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
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


async def get_current_user(request:Request):
    authorization= request.headers.get('Authorization',' ')
    token = None
    if authorization.startswith('Bearer '):
        token = authorization.split(" ", 1)[1]
    token =(token  or request.cookies.get("accessToken")
            or request.cookies.get('token'))
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail= 'token is required')
    # now we have to verify jwt
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='access token is required',
            )
        user_id = ObjectId(decoded['id'])
        session_id = ObjectId(decoded['sessionId'])
    except (InvalidTokenError, InvalidId, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired access token',
        )
    
    



