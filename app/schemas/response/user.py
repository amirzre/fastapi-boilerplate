from pydantic import UUID4, BaseModel, ConfigDict, Field

from app.models import UserRole


class UserResponse(BaseModel):
    uuid: UUID4 = Field(examples=["a3b8f042-1e16-4f0a-a8f0-421e16df0a2f"])
    email: str = Field(examples=["johndoe@example.com"])
    first_name: str | None = Field(examples=["john"])
    last_name: str | None = Field(examples=["doe"])
    role: UserRole = Field(examples=["USER"])
    activated: bool = Field(examples=[True])

    model_config = ConfigDict(from_attributes=True)
