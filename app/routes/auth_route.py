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
from app.middleware import auth_middleware
from app.schema.user_schema import UserCreate, UserLogin_Schema
from app.schema.auth_schema import RefreshRequest, RefreshResponse
from app.utils.Api_response import ApiResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Register
@router.post(
    "/register",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(create_user_request: UserCreate):
    new_user = await userRegister(create_user_request.model_dump())
    return ApiResponse(
        status="success",
        message="User created",
        data={"user_details": new_user},
    )


# Login
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
    response.set_cookie(
        key="refreshToken",
        value=tokens["refreshToken"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    return login_result


# Refresh & Rotate Token
@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
)
async def rotate_refresh_token(
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
    incoming_token = (
        (data.refreshToken if data else None)
        or refresh_cookie
        or (
            authorization.split(" ", 1)[1]
            if authorization and authorization.lower().startswith("bearer ")
            else None
        )
    )

    if not incoming_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    refresh_result = await userRefreshToken(incoming_token)

    # Set updated cookies for rotated tokens
    response.set_cookie(
        key="accessToken",
        value=refresh_result["accessToken"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=10 * 60,
        path="/",
    )
    response.set_cookie(
        key="refreshToken",
        value=refresh_result["refreshToken"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )

    return refresh_result
