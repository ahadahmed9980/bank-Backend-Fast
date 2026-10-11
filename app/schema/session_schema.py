from pydantic import BaseModel, Field, field_validator, EmailStr
import re
from typing import Optional
from datetime import datetime


class SessionModel(BaseModel):
    userId: str
    refreshTokenHash: str
    ip: str
    userAgent: str
