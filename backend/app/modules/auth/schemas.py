from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.models import UserRole


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")


class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")


class UserSummary(BaseModel):
    id: int
    uuid: UUID
    email: str
    full_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class UserProfileResponse(BaseModel):
    id: int
    uuid: UUID
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "UserSummary",
    "TokenResponse",
    "UserProfileResponse",
]
