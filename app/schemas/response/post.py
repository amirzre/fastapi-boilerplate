from pydantic import UUID4, BaseModel, ConfigDict, Field

from app.models import PostStatus


class PostResponse(BaseModel):
    uuid: UUID4 = Field(examples=["a3b8f042-1e16-4f0a-a8f0-421e16df0a2f"])
    title: str = Field(examples=["First Post"])
    content: str = Field(examples=["Test post content"])
    status: PostStatus = Field(examples=[PostStatus.DRAFT])
    user_id: UUID4 = Field(examples=["a3b8f042-1e16-4f0a-a8f0-421e16df0a2f"])

    model_config = ConfigDict(from_attributes=True)
