from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class AccoutCreate(BaseModel):
    currency: str = Field(default="PKR", min_length=1, max_length=5)


class AccountData(BaseModel):
    id: str
    userId: str
    status: AccountStatus
    currency: str
    createdAt: datetime
    updatedAt: datetime

class AcountResponse(BaseModel):
    status:bool
    message:str
    data:AccountData

class BalanceData(BaseModel):
    accountId: str
    balance: float
    currency: str


class BalanceResponse(BaseModel):
    status: bool
    message: str
    data: BalanceData