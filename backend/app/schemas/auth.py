from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9._-]+$")
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(RegisterRequest):
    pass


class UserRead(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
