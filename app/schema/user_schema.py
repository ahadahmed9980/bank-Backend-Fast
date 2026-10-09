from pydantic import BaseModel, Field, field_validator, EmailStr
import re


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("name is required")
        return value

    # email class method
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()
        return value

    # password class method
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        pattern = (
            r"^(?=.*[A-Za-z])" r"(?=.*\d)" r"(?=.*[@$!%*?&])" r"[A-Za-z\d@$!%*?&]{6,}$"
        )
        if not re.match(pattern, value):
            raise ValueError(
                "Password must be at least 6 characters "
                "and contain letters, numbers, "
                "and a special character"
            )
        return value


class UserLogin(BaseModel):

    email: EmailStr
    password: str = Field(..., min_length=6)

    # email class method
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()
        return value

    # password class method
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        pattern = (
            r"^(?=.*[A-Za-z])" r"(?=.*\d)" r"(?=.*[@$!%*?&])" r"[A-Za-z\d@$!%*?&]{6,}$"
        )
        if not re.match(pattern, value):
            raise ValueError(
                "Password must be at least 6 characters "
                "and contain letters, numbers, "
                "and a special character"
            )
        return value
