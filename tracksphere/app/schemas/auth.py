from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: UserRole


class SessionUser(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    active: bool

    class Config:
        from_attributes = True
