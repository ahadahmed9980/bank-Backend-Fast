import hmac

from bson import ObjectId
from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
    Header,
    Cookie,
    Body,
    HTTPException,
)
import jwt
from app.config import JWT_SECRET, JWT_ALGORITHM
from app.schema.user_schema import UserCreate, UserLogin_Schema
from app.model.user_model import (
    userRegister,
    userLogin,
    getActiveSession,
    rotateRefreshToken_hash,
)
from app.utils.Api_response import ApiResponse
from jwt.exceptions import InvalidTokenError
from app.database.mongodb import users_collection, session_collection
from datetime import datetime, timezone
from app.schema.auth_schema import RefreshResponse, RefreshRequest
from app.utils.tokens import (
    hash_refresh_token,
    creat_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(create_user_request: UserCreate):
    new_user = await userRegister(create_user_request.model_dump())
    return ApiResponse(
        status="success", message="User created", data={" user_details": new_user}
    )


# login
@router.post(
    "/login",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    login_user_request: UserLogin_Schema,
    request: Request,
    response: Response,
):
    login_result = await userLogin(
        data=login_user_request.model_dump(),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    tokens = login_result["data"]["tokens"]
    response.set_cookie(
        key="accessToken",
        value=tokens["accessToken"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=10 * 60,
        path="/",
    )
    return login_result


# new access and rotate refresh token
@router.post("/refresh", response_model=RefreshResponse)
async def roate_refreshToken(
    response: Response,
    data: RefreshRequest | None = Body(default=None),
    refresh_cookie: str | None = Cookie(
        default=None,
        alias="refreshToken",
    ),
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
    ),
):
    incommingToken = (
        (data.refreshToken if data else None)
        or refresh_cookie
        or (
            authorization.split(" ", 1)[1]
            if authorization and authorization.lower().startswith("bearer ")
            else None
        )
    )
    # if not refresh token
    if not incommingToken:
        raise HTTPException(
            status_code=401,
            detail="Refresh token required",
        )
    # verify token
    try:
        decoded = jwt.decode(
    incommingToken,
    JWT_SECRET,
    algorithms=[JWT_ALGORITHM],
)
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
            )
        user_id = ObjectId(decoded["id"])
        session_id = ObjectId(decoded["sessionId"])
    except HTTPException:
        raise

    except (InvalidTokenError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )
    # is user exist or not
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    # 4. Session active hai ya revoke ho chuka hai
    session = await getActiveSession(
        user_id,
        session_id,
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or revoked session",
        )
    incoming_hash = hash_refresh_token(incommingToken)
    stored_hash = session.get("refreshTokenHash")
    # compare both hash
    if not stored_hash or not hmac.compare_digest(stored_hash, incoming_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token hash",
        )
    # gen new refresh token
    new_access_token = creat_access_token(
        user_id,
        session_id,
    )
    new_refresh_token = create_refresh_token(
        user_id,
        session_id,
    )
    new_hash = hash_refresh_token(new_refresh_token)
    rotated = await rotateRefreshToken_hash(
        user_id,
        session_id,
        stored_hash,
        new_hash,
    )
    if not rotated:
        raise HTTPException(
            status_code=401,
            detail="Refresh token already used",
        )
    response.set_cookie(
        key="refreshToken",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Local HTTP only; production HTTPS par True
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    return {
        "message": "Access token refreshed successfully",
        "accessToken": new_access_token,
        "refreshTken":new_refresh_token
    }
