from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid work/personal email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password with minimum 8 characters")
    role: Optional[UserRole] = Field(default=UserRole.USER, description="User role assignment")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, max_length=72, description="User password")


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsersListResponse(BaseModel):
    users: List[UserSummary]
    total: int


class UserPasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=72, description="Current user password")
    new_password: str = Field(..., min_length=8, max_length=72, description="New password with minimum 8 characters")
