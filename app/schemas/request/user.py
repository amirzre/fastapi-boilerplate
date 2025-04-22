from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.extra import BaseFilterParams
from core.utils import PasswordValidator


class RegisterUserRequest(BaseModel):
    email: EmailStr = Field(description="Email")
    first_name: str | None = Field(max_length=50, description="Firstname")
    last_name: str | None = Field(max_length=50, description="Lastname")
    role: UserRole | None = Field(description="User Role")
    activated: bool = Field(description="activated")
    password: PasswordValidator = Field(max_length=50, min_length=8, description="Password")


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = Field(None, description="Email")
    first_name: str | None = Field(None, max_length=50, description="Firstname")
    last_name: str | None = Field(None, max_length=50, description="Lastname")
    password: PasswordValidator | None = Field(None, max_length=50, min_length=8, description="Password")


class UserFilterParams(BaseFilterParams):
    email: EmailStr | None = Field(None)
    role: UserRole | None = Field(None)
    activated: bool = Field(None)
    created_from: datetime | None = Field(None)
    created_to: datetime | None = Field(None)
    updated_from: datetime | None = Field(None)
    updated_to: datetime | None = Field(None)

    model_config = {"extra": "forbid"}
