from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.middleware.auth_middleware import get_current_user
from app.schema.account_schema import (AccoutCreate, AccountResponse )
from app.model.account_model import CreateAccout

router = APIRouter(prefix="/api/account", tags=["Accounts"])


# create account
@router.post('/create', response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccoutCreate,
    user: dict = Depends(get_current_user),
):
    user_id = user['_id']
    account = await CreateAccout(user_id=user_id, currency=data.currency)
    if account is None :
            raise HTTPException (status_code= 401, detail='account not found')
    return {
        "message": "Account created successfully",
        "account": account,
    }
    


