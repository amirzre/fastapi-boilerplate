from typing import Sequence

from pydantic import UUID4

from app.models import Post
from app.schemas.request import PostFilterParams
from core.repository import BaseRepository


class PostRepository(BaseRepository[Post]):
    """
    Repository class that handles all database operations related to the Post model.
    """

    async def get_by_uuid(self, uuid: UUID4) -> Post | None:
        """
        Retrieve a post by its UUID.

        Args:
            uuid (UUID4): The UUID of the post to retrieve.

        Returns:
            Post | None: The post instance if found; otherwise, None.
        """
        query = self._query()
        query = query.filter(Post.uuid == uuid)

        return await self._one_or_none(query)

    async def get_posts_by_user(self, user_id: UUID4, filter_params: PostFilterParams) -> tuple[Sequence[Post], int]:
        """
        Retrieve posts created by a specific user, with optional filtering and pagination.

        Args:
            user_id (UUID4): UUID of the user whose posts are to be retrieved.
            filter_params (PostFilterParams): Filtering and pagination parameters.

        Returns:
            tuple[Sequence[Post], int]: A tuple containing the list of filtered posts and the total count.
        """
        query = self._query().filter(Post.user_id == user_id)

        if filter_params.title:
            query = query.filter(Post.title.icontains(filter_params.title))
        if filter_params.status:
            query = query.filter(Post.status == filter_params.status)
        if filter_params.created_from:
            query = query.filter(Post.created >= filter_params.created_from)
        if filter_params.created_to:
            query = query.filter(Post.created <= filter_params.created_to)
        if filter_params.updated_from:
            query = query.filter(Post.updated >= filter_params.updated_from)
        if filter_params.updated_to:
            query = query.filter(Post.updated <= filter_params.updated_to)

        order_column = Post.created if filter_params.order_by == "created" else Post.updated
        query = query.order_by(order_column)

        paginated_query = query.limit(filter_params.limit).offset(filter_params.offset)

        posts = await self._all(query=paginated_query)
        total = await self._count(query=query)

        return posts, total
