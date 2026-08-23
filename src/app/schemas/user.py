from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
    active: bool | None = None
    password: str | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
