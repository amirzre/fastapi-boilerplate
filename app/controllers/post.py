from pydantic import UUID4

from app.models import Post
from app.repositories import PostRepository, UserRepository
from app.schemas.extra import PaginationResponse
from app.schemas.request import CreatePostRequest, PostFilterParams, UpdatePostRequest
from app.schemas.response import PostResponse
from core.controller import BaseController
from core.db import Transactional
from core.exceptions import NotFoundException
from core.i18n import translate as _
from core.security import ACLRegistry


class PostController(BaseController[Post]):
    """Post controller provides all the logic operations for the Post model."""

    def __init__(self, post_repository: PostRepository, user_repository: UserRepository):
        """
        Initialize the PostController with the required repositories.

        :param post_repository: Repository for handling Post model operations.
        :param user_repository: Repository for handling User model operations.
        """
        super().__init__(model=Post, repository=post_repository)
        self.post_repository = post_repository
        self.user_repository = user_repository

    async def get_user_posts(
        self, *, user_id: UUID4, filter_params: PostFilterParams
    ) -> PaginationResponse[PostResponse]:
        """
        Retrieve all posts created by a specific user with optional filters.

        :param user_id: UUID of the user whose posts are to be retrieved.
        :param filter_params: Filters for pagination, title, status, and timestamps.
        :return: A pagination response containing the user's posts.
        :raises NotFoundException: If the user with the given UUID does not exist.
        """
        user = await self.user_repository.get_by_uuid(uuid=user_id)
        if not user:
            raise NotFoundException(message=_("User not found."))

        posts, total = await self.post_repository.get_posts_by_user(user_id=user.uuid, filter_params=filter_params)

        [ACLRegistry.set_acl(post.uuid, post.__acl__()) for post in posts]

        return PaginationResponse[PostResponse](
            limit=filter_params.limit,
            offset=filter_params.offset,
            total=total,
            items=[PostResponse.model_validate(post) for post in posts],
        )

    async def get_post(self, *, post_uuid: UUID4) -> PostResponse:
        """
        Retrieve a single post by its UUID.

        :param post_uuid: UUID of the post to be retrieved.
        :return: A response object containing post details.
        :raises NotFoundException: If the post with the given UUID does not exist.
        """
        post = await self.post_repository.get_by_uuid(uuid=post_uuid)
        if not post:
            raise NotFoundException(message=_("Post not found."))

        acl = post.__acl__()
        ACLRegistry.set_acl(resource_id=post.uuid, acl=acl)

        return PostResponse(
            uuid=post.uuid,
            title=post.title,
            status=post.status,
            user_id=post.user_id,
        )

    @Transactional()
    async def create_post(self, *, create_post_request: CreatePostRequest) -> PostResponse:
        """
        Create a new post for a specific user.

        :param create_post_request: Request object containing post details and the user UUID.
        :return: A response object containing details of the newly created post.
        :raises NotFoundException: If the user with the given UUID does not exist.
        """
        user = await self.user_repository.get_by_uuid(uuid=create_post_request.user_id)
        if not user:
            raise NotFoundException(message=_("User not found."))

        created_post = await self.post_repository.create(attributes=create_post_request)

        acl = created_post.__acl__()
        ACLRegistry.set_acl(resource_id=created_post.uuid, acl=acl)

        return PostResponse(
            uuid=created_post.uuid,
            title=created_post.title,
            status=created_post.status,
            user_id=created_post.user_id,
        )

    @Transactional()
    async def update_post(self, *, post_uuid: UUID4, update_post_request: UpdatePostRequest) -> PostResponse:
        """
        Update an existing post by its UUID.

        :param post_uuid: UUID of the post to be updated.
        :param update_post_request: Request object containing the updated post details.
        :return: A response object containing the updated post details.
        :raises NotFoundException: If the post with the given UUID does not exist.
        """
        post = await self.post_repository.get_by_uuid(uuid=post_uuid)
        if not post:
            raise NotFoundException(message=_("Post not found."))

        updated_post = await self.post_repository.update(model=post, attributes=update_post_request)

        acl = updated_post.__acl__()
        ACLRegistry.set_acl(resource_id=updated_post.uuid, acl=acl)

        return PostResponse(
            uuid=updated_post.uuid,
            title=updated_post.title,
            status=updated_post.status,
            user_id=updated_post.user_id,
        )

    @Transactional()
    async def delete_post(self, *, post_uuid: UUID4) -> None:
        """
        Delete an existing post by its UUID.

        :param post_uuid: UUID of the post to be deleted.
        :return: None.
        :raises NotFoundException: If the post with the given UUID does not exist.
        """
        post = await self.post_repository.get_by_uuid(uuid=post_uuid)
        if not post:
            raise NotFoundException(message=_("Post not found."))

        acl = post.__acl__()
        ACLRegistry.set_acl(resource_id=post.uuid, acl=acl)

        return await self.post_repository.delete(model=post)
