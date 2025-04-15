from typing import Sequence

from pydantic import UUID4

from app.models import Post
from app.schemas.request import PostFilterParams
from core.repository import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Post repository provides all the database operations for the Post model."""

    async def get_by_uuid(self, uuid: UUID4) -> Post | None:
        """
        Get Post by UUID.

        param uuid: Post UUID.
        return: Post or None.
        """
        query = self._query()
        query = query.filter(Post.uuid == uuid)

        return await self._one_or_none(query)

    async def get_posts_by_user(self, user_id: UUID4, filter_params: PostFilterParams) -> tuple[Sequence[Post], int]:
        """
        Get Posts by User ID with optional filters and return the total count.

        :param user_id: User ID.
        :param filter_params: Post filter parameters.
        :return: A tuple of list of posts and the total count of matching posts.
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
