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
    """
    Controller responsible for handling business logic related to the Post model.
    """

    def __init__(self, post_repository: PostRepository, user_repository: UserRepository):
        """
        Initialize the PostController with necessary repositories.

        Args:
            post_repository (PostRepository): Repository for Post model operations.
            user_repository (UserRepository): Repository for User model operations.
        """
        super().__init__(model=Post, repository=post_repository)
        self.post_repository = post_repository
        self.user_repository = user_repository

    async def get_user_posts(
        self, *, user_id: UUID4, filter_params: PostFilterParams
    ) -> PaginationResponse[PostResponse]:
        """
        Retrieve posts created by a specific user, optionally filtered and paginated.

        Args:
            user_id (UUID4): UUID of the user whose posts are to be fetched.
            filter_params (PostFilterParams): Filters for pagination, title, status, and timestamps.

        Returns:
            PaginationResponse[PostResponse]: Paginated list of post responses.

        Raises:
            NotFoundException: If the specified user does not exist.
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

        Args:
            post_uuid (UUID4): UUID of the post to retrieve.

        Returns:
            PostResponse: Post data in response format.

        Raises:
            NotFoundException: If the post does not exist.
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
        Create a new post.

        Args:
            create_post_request (CreatePostRequest): Input data for creating the post.

        Returns:
            PostResponse: Created post response.

        Raises:
            NotFoundException: If the associated user does not exist.
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
        Update an existing post.

        Args:
            post_uuid (UUID4): UUID of the post to update.
            update_post_request (UpdatePostRequest): Fields to update in the post.

        Returns:
            PostResponse: Updated post response.

        Raises:
            NotFoundException: If the post does not exist.
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
    async def delete_post(self, *, post_uuid: UUID4) -> PostResponse:
        """
        Delete a post by its UUID.

        Args:
            post_uuid (UUID4): UUID of the post to delete.

        Returns:
            PostResponse: Deleted post response.

        Raises:
            NotFoundException: If the post does not exist.
        """
        post = await self.post_repository.get_by_uuid(uuid=post_uuid)
        if not post:
            raise NotFoundException(message=_("Post not found."))

        acl = post.__acl__()
        ACLRegistry.set_acl(resource_id=post.uuid, acl=acl)

        deleted_post = await self.post_repository.delete(model=post)

        return PostResponse(
            uuid=deleted_post.uuid,
            title=deleted_post.title,
            status=deleted_post.status,
            user_id=deleted_post.user_id,
        )
