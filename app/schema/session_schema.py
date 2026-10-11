from typing import Optional
from pydantic import BaseModel


class SessionModel(BaseModel):
    userId: str
    refreshTokenHash: Optional[str] = None
    ip: Optional[str] = None
    userAgent: Optional[str] = None
