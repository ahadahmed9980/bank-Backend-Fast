from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refreshToken: str | None = None


class RefreshResponse(BaseModel):
    message: str
    accessToken: str
    refreshToken: str
