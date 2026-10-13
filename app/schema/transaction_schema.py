from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"

class TransactionCreate(BaseModel):
    fromAccount:str
    toAccount:str
    amount:float=Field(gt=0)
    idempotanceKey:str=Field(min_length=5)

class TransactionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    message: str
    transaction: dict