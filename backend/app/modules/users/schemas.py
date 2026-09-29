from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.models import UserRole


class UserBase(BaseModel):
    email: str = Field(..., max_length=255, description="Email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role (teacher/student)")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plain text password")


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
]

