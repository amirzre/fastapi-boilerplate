from typing import Literal
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole


class BaseFilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created", "updated"] = "created"


class UserFilterParams(BaseFilterParams):
    email: EmailStr | None = Field(None)
    role: UserRole | None = Field(None)
    activated: bool = Field(None)
    created_from: datetime | None = Field(None)
    created_to: datetime | None = Field(None)
    updated_from: datetime | None = Field(None)
    updated_to: datetime | None = Field(None)

    model_config = {"extra": "forbid"}
