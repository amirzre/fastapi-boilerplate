from pydantic import UUID4, BaseModel, Field

from app.models import PostStatus


class CreatePostRequest(BaseModel):
    title: str = Field(max_length=200, description="Post title")
    content: str = Field(description="Post content")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Post status")
    user_id: UUID4 = Field(description="Related user UUID")
