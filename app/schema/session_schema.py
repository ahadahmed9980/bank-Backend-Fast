from pydantic import BaseModel, Field, field_validator, EmailStr
import re
from typing import Optional
from datetime import datetime


class SessionModel(BaseModel):
    userId: str
    refreshTokenHash: str
    ip: str
    userAgent: str


class SessionResponse(BaseModel):
    id: str
    userId: str
    ip: str
    userAgent: str
    revoke: bool = False
    accessToken: str
    refreshToken: str
    revokedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
