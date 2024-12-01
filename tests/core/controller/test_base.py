from contextvars import ContextVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from core.controller import BaseController
from core.exceptions import NotFoundException


@pytest.mark.asyncio
class TestBaseController:
    """Test suite for the BaseController class."""

    @pytest.fixture
    def mock_session(self):
        """
        Mocks the session context for transactional operations.
        """
        mock_session = AsyncMock()
        session_context = ContextVar("session_context")
        session_context.set(mock_session)
        return mock_session

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Sets up the necessary mocks and dependencies for each test.
        """
        # Mock the model and repository
        self.mock_model = MagicMock()
        self.mock_model.__tablename__ = "test_model"
        self.mock_repository = AsyncMock()

        self.controller = BaseController(model=self.mock_model, repository=self.mock_repository)

    async def test_get_by_id_success(self):
        """
        Test that `get_by_id` successfully retrieves an object by its ID.
        """
        mock_object = MagicMock()
        self.mock_repository.get_by.return_value = mock_object

        result = await self.controller.get_by_id(1)

        self.mock_repository.get_by.assert_awaited_once_with(field="id", value=1, unique=True)
        assert result == mock_object

    async def test_get_by_id_not_found(self):
        """
        Test that `get_by_id` raises NotFoundException when no object is found.
        """
        self.mock_repository.get_by.return_value = None

        with pytest.raises(NotFoundException):
            await self.controller.get_by_id(1)

    async def test_get_by_uuid_success(self):
        """
        Test that `get_by_uuid` successfully retrieves an object by its UUID.
        """
        uuid = uuid4()
        mock_object = MagicMock()
        self.mock_repository.get_by.return_value = mock_object

        result = await self.controller.get_by_uuid(uuid)

        self.mock_repository.get_by.assert_awaited_once_with(field="uuid", value=uuid, unique=True)
        assert result == mock_object

    async def test_get_by_uuid_not_found(self):
        """
        Test that `get_by_uuid` raises NotFoundException when no object is found.
        """
        uuid = uuid4()
        self.mock_repository.get_by.return_value = None

        with pytest.raises(NotFoundException):
            await self.controller.get_by_uuid(uuid)

    async def test_get_all(self):
        """
        Test that `get_all` returns a paginated list of objects.
        """
        mock_objects = [MagicMock(), MagicMock()]
        self.mock_repository.get_all.return_value = mock_objects

        result = await self.controller.get_all(skip=10, limit=5)

        self.mock_repository.get_all.assert_awaited_once_with(10, 5)
        assert result == mock_objects

    async def test_create(self, mock_session):
        """
        Test that `create` creates a new object using the repository.
        """
        mock_attributes = {"name": "Test Object"}
        mock_object = MagicMock()
        self.mock_repository.create.return_value = mock_object

        with patch("core.db.transactional.session", mock_session):
            result = await self.controller.create(mock_attributes)

        self.mock_repository.create.assert_awaited_once_with(mock_attributes)
        mock_session.commit.assert_awaited_once()
        assert result == mock_object

    async def test_delete(self, mock_session):
        """
        Test that `delete` deletes an object using the repository.
        """
        mock_object = MagicMock()
        self.mock_repository.delete.return_value = True

        with patch("core.db.transactional.session", mock_session):
            result = await self.controller.delete(mock_object)

        self.mock_repository.delete.assert_awaited_once_with(mock_object)
        mock_session.commit.assert_awaited_once()
        assert result is True
