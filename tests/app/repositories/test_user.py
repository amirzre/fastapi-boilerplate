from unittest.mock import ANY, AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models import User, UserRole
from app.repositories import UserRepository
from app.schemas.request import UserFilterParams


@pytest.mark.asyncio
class TestUserRepository:
    """
    Test suite for the UserRepository class.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Set up the necessary dependencies for each test.
        """
        self.mock_db_session = MagicMock()

        self.mock_query = MagicMock()
        self.mock_query.filter = MagicMock(return_value=self.mock_query)
        self.mock_query.order_by = MagicMock(return_value=self.mock_query)
        self.mock_query.limit = MagicMock(return_value=self.mock_query)
        self.mock_query.offset = MagicMock(return_value=self.mock_query)
        self.mock_one_or_none = AsyncMock()
        self.mock_all = AsyncMock()
        self.mock_count = AsyncMock()

        self.repository = UserRepository(User, db_session=self.mock_db_session)
        self.repository._query = MagicMock(return_value=self.mock_query)
        self.repository._one_or_none = self.mock_one_or_none
        self.repository._all = self.mock_all
        self.repository._count = self.mock_count

    async def test_get_by_email_success(self):
        """
        Test that `get_by_email` returns the user when a matching email is found.
        """
        mock_user = MagicMock()
        self.mock_one_or_none.return_value = mock_user
        email = "test@example.com"

        result = await self.repository.get_by_email(email)

        self.mock_query.filter.assert_called_once_with(ANY)
        self.mock_one_or_none.assert_awaited_once_with(self.mock_query)

        assert result == mock_user

    async def test_get_by_email_not_found(self):
        """
        Test that `get_by_email` returns None when no user matches the email.
        """
        self.mock_one_or_none.return_value = None
        email = "nonexistent@example.com"

        result = await self.repository.get_by_email(email)

        self.mock_query.filter.assert_called_once_with(ANY)
        self.mock_one_or_none.assert_awaited_once_with(self.mock_query)

        assert result is None

    async def test_get_by_uuid_success(self):
        """
        Test that `get_by_uuid` returns the user when a matching UUID is found.
        """
        mock_user = MagicMock()
        self.mock_one_or_none.return_value = mock_user
        user_uuid = uuid4()

        result = await self.repository.get_by_uuid(user_uuid)

        self.mock_query.filter.assert_called_once_with(ANY)
        self.mock_one_or_none.assert_awaited_once_with(self.mock_query)

        assert result == mock_user

    async def test_get_by_uuid_not_found(self):
        """
        Test that `get_by_uuid` returns None when no user matches the UUID.
        """
        self.mock_one_or_none.return_value = None
        user_uuid = uuid4()

        result = await self.repository.get_by_uuid(user_uuid)

        self.mock_query.filter.assert_called_once_with(ANY)
        self.mock_one_or_none.assert_awaited_once_with(self.mock_query)

        assert result is None

    async def test_get_filtered_users(self):
        """
        Test that `get_filtered_users` returns a filtered list of users and total count.
        """
        mock_users = [MagicMock(), MagicMock()]
        total_count = 2
        self.mock_all.return_value = mock_users
        self.mock_count.return_value = total_count

        filter_params = UserFilterParams(
            email="test@example.com",
            role=UserRole.ADMIN,
            activated=True,
            created_from=None,
            created_to=None,
            updated_from=None,
            updated_to=None,
            order_by="created",
            limit=10,
            offset=0,
        )

        result = await self.repository.get_filtered_users(filter_params)

        self.mock_query.filter.assert_any_call(ANY)
        self.mock_query.order_by.assert_called_once_with(User.created)
        self.mock_all.assert_awaited_once_with(query=self.mock_query)
        self.mock_count.assert_awaited_once_with(query=self.mock_query)

        assert result == (mock_users, total_count)
