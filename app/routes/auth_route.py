from fastapi import APIRouter, status
from app.schema.user_schema import UserCreate
from app.model.user_model import userRegister
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
