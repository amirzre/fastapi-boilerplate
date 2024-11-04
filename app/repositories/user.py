from uuid import UUID

from app.models import User
from app.schemas.extra import UserFilterParams
from core.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User repository provides all the database operations for the User model.
    """

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        :param email: Email.
        :return: User.
        """
        query = self._query()
        query = query.filter(User.email == email)

        return await self._one_or_none(query)

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        """
        Get user by uuid.

        :param uuid: User uuid.
        :return: User.
        """
        query = self._query()
        query = query.filter(User.uuid == uuid)

        return await self._one_or_none(query)

    async def get_filtered_users(self, filter_params: UserFilterParams) -> list[User] | None:
        """
        Get users by filter.

        :param filter_params: user filter parameters.
        :return: list of users.
        """
        query = self._query()

        if filter_params.email:
            query = query.filter(User.email == filter_params.email)
        if filter_params.role:
            query = query.filter(User.role == filter_params.role)
        if filter_params.activated:
            query = query.filter(User.activated == filter_params.activated)

        if filter_params.created_from:
            query = query.where(User.created >= filter_params.created_from)
        if filter_params.created_to:
            query = query.where(User.created <= filter_params.created_to)

        if filter_params.updated_from:
            query = query.where(User.updated >= filter_params.updated_from)
        if filter_params.updated_to:
            query = query.where(User.updated <= filter_params.updated_to)

        order_column = User.created if filter_params.order_by == "created" else User.updated
        query = query.order_by(order_column)

        query = query.limit(filter_params.limit).offset(filter_params.offset)

        return await self._all(query=query)
