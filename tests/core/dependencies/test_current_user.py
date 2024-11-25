from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials

from app.controllers import UserController
from app.repositories import UserRepository
from core.exceptions import BadRequestException
from core.fastapi.dependencies.authentication import AuthenticationHandler
from core.fastapi.dependencies.current_user import (
    get_authenticated_user,
    get_current_user,
    get_current_user_with_refresh_token,
)


@pytest.mark.asyncio
class TestCurrentUser:
    @pytest.fixture
    def mock_request(self):
        """Fixture to create a mocked FastAPI `Request` object with a fake cookie."""
        req = MagicMock(spec=Request)
        req.cookies = {"Access-Token": "fake_access_token"}
        return req

    @pytest.fixture
    def mock_authentication_handler(self, mock_request):
        """Fixture to mock the `AuthenticationHandler` with the request fixture."""
        handler = AuthenticationHandler(mock_request)
        return AsyncMock(wraps=handler)

    @patch("core.fastapi.dependencies.authentication.AuthenticationHandler.authenticate_user", new_callable=AsyncMock)
    async def test_get_authenticated_user(self, mock_authenticate_user, mock_request):
        """Test that `get_authenticated_user` successfully retrieves a user UUID when a valid access token is provided."""
        mock_authenticate_user.return_value = "user-uuid"

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake_access_token")

        user_uuid = await get_authenticated_user(mock_request, credentials)

        assert user_uuid == "user-uuid"
        mock_authenticate_user.assert_awaited_once_with(token_type="Access", key="uuid", credentials=credentials)

    @patch("core.fastapi.dependencies.authentication.AuthenticationHandler.authenticate_user", new_callable=AsyncMock)
    @patch.object(UserController, "get_by_uuid", new_callable=AsyncMock)
    async def test_get_current_user(self, mock_get_by_uuid, mock_authenticate_user, mock_request):
        """Test that `get_current_user` successfully retrieves the current user when the user is active."""
        mock_authenticate_user.return_value = "user-uuid"
        mock_get_by_uuid.return_value = AsyncMock(activated=True)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake_access_token")

        mock_user_repository = AsyncMock(spec=UserRepository)
        user_controller = UserController(user_repository=mock_user_repository)

        user = await get_current_user(mock_request, token=credentials, user_controller=user_controller)

        assert user.activated
        mock_authenticate_user.assert_awaited_once_with(token_type="Access", key="uuid", credentials=credentials)
        mock_get_by_uuid.assert_awaited_once_with(uuid="user-uuid")

    @patch("core.fastapi.dependencies.authentication.AuthenticationHandler.authenticate_user", new_callable=AsyncMock)
    @patch.object(UserController, "get_by_uuid", new_callable=AsyncMock)
    async def test_get_current_user_inactive(self, mock_get_by_uuid, mock_authenticate_user, mock_request):
        """Test that `get_current_user` raises a `BadRequestException` when the user is inactive."""
        mock_authenticate_user.return_value = "user-uuid"
        mock_get_by_uuid.return_value = AsyncMock(activated=False)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake_access_token")

        mock_user_repository = AsyncMock(spec=UserRepository)
        user_controller = UserController(user_repository=mock_user_repository)

        with pytest.raises(BadRequestException):
            await get_current_user(mock_request, token=credentials, user_controller=user_controller)

        mock_authenticate_user.assert_awaited_once_with(token_type="Access", key="uuid", credentials=credentials)
        mock_get_by_uuid.assert_awaited_once_with(uuid="user-uuid")

    @patch("core.fastapi.dependencies.authentication.AuthenticationHandler.authenticate_user", new_callable=AsyncMock)
    async def test_get_current_user_with_refresh_token(self, mock_authenticate_user, mock_request):
        """Test that `get_current_user_with_refresh_token` successfully retrieves a user UUID when a valid refresh token is provided."""
        mock_authenticate_user.return_value = "verify-uuid"

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake_refresh_token")

        user_uuid = await get_current_user_with_refresh_token(mock_request, token=credentials)

        assert user_uuid == "verify-uuid"
        mock_authenticate_user.assert_awaited_once_with(token_type="Refresh", key="verify", credentials=credentials)
