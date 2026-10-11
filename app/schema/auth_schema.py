from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refreshToken: str


class RefreshResponse(BaseModel):
    message: str
    accessToken: str
    refreshToken: str
