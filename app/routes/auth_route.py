from fastapi import APIRouter, status , Request
from app.schema.user_schema import UserCreate, UserLogin_Schema
from app.model.user_model import userRegister, userLogin
from app.utils.Api_response import ApiResponse 

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
):
    login_result = await userLogin(
        data=login_user_request.model_dump(),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return login_result
