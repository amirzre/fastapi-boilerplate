from pydantic import UUID4
from sqlalchemy import select

from app.models import Post, User
from core.repository import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Post repository provides all the database operations for the Post model."""

    async def get_user_by_uuid(self, uuid: UUID4) -> User | None:
        """
        Get User by UUID.

        param uuid: User UUID.
        return : User or None.
        """
        query = select(User).filter(User.uuid == uuid)

        return await self._one_or_none(query)
