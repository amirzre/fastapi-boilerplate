from app.models import Post
from app.repositories import PostRepository
from app.schemas.request import CreatePostRequest
from app.schemas.response import PostResponse
from core.controller import BaseController
from core.db import Transactional
from core.exceptions import NotFoundException
from core.i18n import translate as _


class PostController(BaseController[Post]):
    """Post controller provides all the logic operations for the Post model."""

    def __init__(self, post_repository: PostRepository):
        super().__init__(model=Post, repository=post_repository)
        self.post_repository = post_repository

    @Transactional()
    async def create_post(self, *, create_post_request: CreatePostRequest) -> PostResponse:
        user = await self.post_repository.get_user_by_uuid(uuid=create_post_request.user_id)
        if not user:
            raise NotFoundException(message=_("User not found."))

        created_post = await self.post_repository.create(attributes=create_post_request)

        return PostResponse(
            uuid=created_post.uuid,
            title=created_post.title,
            status=created_post.status,
            user_id=created_post.user_id,
        )
