from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.controllers import UserController
from app.models import UserRole
from app.schemas.extra import PaginationResponse, UserFilterParams
from app.schemas.request import RegisterUserRequest, UpdateUserRequest
from app.schemas.response import UserResponse
from core.exceptions import BadRequestException, NotFoundException


@pytest.mark.asyncio
class TestUserController:
    @pytest.fixture
    def user_repository_mock(self):
        """Fixture to mock the UserRepository class."""
        return AsyncMock()

    @pytest.fixture
    def user_controller(self, user_repository_mock):
        """Fixture to initialize the UserController with a mocked repository."""
        return UserController(user_repository=user_repository_mock)

    async def test_get_filtered_user_success(self, user_controller, user_repository_mock):
        """Test retrieving users with filter parameters successfully."""
        filter_params = UserFilterParams(limit=10, offset=0, email="test@example.com")
        mocked_users = [
            UserResponse(
                uuid=uuid4(),
                email="test@example.com",
                first_name="Test",
                last_name="User",
                role=UserRole.USER,
                activated=True,
            )
        ]
        user_repository_mock.get_filtered_users.return_value = (mocked_users, 1)

        response = await user_controller.get_filtered_user(filter_params=filter_params)

        assert isinstance(response, PaginationResponse)
        assert response.total == 1
        assert response.items == mocked_users

    async def test_get_user_success(self, user_controller, user_repository_mock):
        """Test retrieving a user by UUID successfully."""
        user_uuid = uuid4()
        mocked_user = AsyncMock(
            uuid=user_uuid,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            activated=True,
        )
        user_repository_mock.get_by_uuid.return_value = mocked_user

        response = await user_controller.get_user(user_uuid=user_uuid)

        assert isinstance(response, UserResponse)
        assert response.uuid == user_uuid
        assert response.email == "test@example.com"

    async def test_get_user_not_found(self, user_controller, user_repository_mock):
        """Test retrieving a user by UUID when the user does not exist."""
        user_repository_mock.get_by_uuid.return_value = None

        with pytest.raises(NotFoundException):
            await user_controller.get_user(user_uuid=uuid4())

    async def test_register_user_success(self, user_controller, user_repository_mock):
        """Test successful user registration."""
        register_request = RegisterUserRequest(
            email="newuser@example.com",
            password="Password@123",
            first_name="New",
            last_name="User",
            role=UserRole.USER,
            activated=True,
        )
        mocked_created_user = AsyncMock(
            uuid=uuid4(),
            email=register_request.email,
            first_name=register_request.first_name,
            last_name=register_request.last_name,
            role=UserRole.USER,
            activated=True,
        )
        user_repository_mock.get_by_email.return_value = None
        user_repository_mock.create.return_value = mocked_created_user

        with patch("core.security.PasswordHandler.hash", return_value="hashed_password"):
            with patch("core.db.session.session_context", new_callable=AsyncMock):
                response = await user_controller.register_user(register_user_request=register_request)

        assert isinstance(response, UserResponse)
        assert response.email == register_request.email

    async def test_register_user_already_exists(self, user_controller, user_repository_mock):
        """Test user registration when the user already exists."""
        register_request = RegisterUserRequest(
            email="existing@example.com",
            password="Password@123",
            first_name="Existing",
            last_name="User",
            role=UserRole.USER,
            activated=True,
        )
        user_repository_mock.get_by_email.return_value = AsyncMock()

        with patch("core.db.session.session_context", new_callable=AsyncMock):
            with pytest.raises(BadRequestException):
                await user_controller.register_user(register_user_request=register_request)

    async def test_update_user_success(self, user_controller, user_repository_mock):
        """Test updating a user successfully."""
        user_uuid = uuid4()
        update_request = UpdateUserRequest(first_name="Updated name", last_name="Updated family")
        mocked_user = AsyncMock(
            uuid=user_uuid,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            activated=True,
        )
        updated_user = AsyncMock(
            uuid=user_uuid,
            email="test@example.com",
            first_name="Updated name",
            last_name="Updated family",
            role=UserRole.USER,
            activated=True,
        )
        user_repository_mock.get_by_uuid.return_value = mocked_user
        user_repository_mock.update.return_value = updated_user

        with patch("core.db.session.session_context", new_callable=AsyncMock):
            response = await user_controller.update_user(user_uuid=user_uuid, update_user_request=update_request)

        assert isinstance(response, UserResponse)
        assert response.first_name == "Updated name"

    async def test_delete_user_success(self, user_controller, user_repository_mock):
        """Test deleting a user successfully."""
        user_uuid = uuid4()
        mocked_user = AsyncMock(uuid=user_uuid)
        user_repository_mock.get_by_uuid.return_value = mocked_user

        await user_controller.delete_user(user_uuid=user_uuid)

        user_repository_mock.delete.assert_called_once_with(model=mocked_user)

    async def test_delete_user_not_found(self, user_controller, user_repository_mock):
        """Test deleting a user that does not exist."""
        user_repository_mock.get_by_uuid.return_value = None

        with pytest.raises(NotFoundException):
            await user_controller.delete_user(user_uuid=uuid4())
