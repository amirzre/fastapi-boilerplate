from unittest.mock import AsyncMock, patch

import pytest

from app.controllers import AuthController
from app.schemas.extra import Token
from app.schemas.request import UserLoginRequest
from core.exceptions import BadRequestException, NotFoundException, UnauthorizedException


@pytest.mark.asyncio
class TestAuthController:
    @pytest.fixture
    def mock_user_repository(self):
        """Fixture to mock UserRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_cache(self):
        """Fixture to mock Redis cache."""
        return AsyncMock()

    @pytest.fixture
    def auth_controller(self, mock_user_repository):
        """Fixture to create an AuthController instance."""
        return AuthController(user_repository=mock_user_repository)

    async def test_login_success(self, auth_controller, mock_user_repository, mock_cache):
        """Test successful login."""
        mock_user = AsyncMock()
        mock_user.password = "hashed_password"
        mock_user.uuid = "test-uuid"
        mock_user.role = "user"
        mock_user.activated = True

        mock_user_repository.get_by_email.return_value = mock_user

        with patch("core.security.PasswordHandler.verify", return_value=True):
            with patch("core.security.JWTHandler.encode", return_value="access_token"):
                with patch("core.security.JWTHandler.encode_refresh_token", return_value="refresh_token"):
                    response = await auth_controller.login(
                        login_user_request=UserLoginRequest(email="test@example.com", password="password"),
                        cache=mock_cache,
                    )

                    assert isinstance(response, Token)
                    assert response.access_token == "access_token"
                    assert response.refresh_token == "refresh_token"
                    mock_cache.set.assert_called_once()

    async def test_login_invalid_credentials(self, auth_controller, mock_user_repository, mock_cache):
        """Test login with invalid credentials."""
        mock_user_repository.get_by_email.return_value = None

        with pytest.raises(BadRequestException):
            await auth_controller.login(
                login_user_request=UserLoginRequest(email="invalid@example.com", password="password"),
                cache=mock_cache,
            )

    async def test_refresh_token_success(self, auth_controller, mock_user_repository, mock_cache):
        """Test successful refresh token."""
        mock_user = AsyncMock()
        mock_user.uuid = "test-uuid"
        mock_user.role = "user"
        mock_user_repository.get_by_uuid.return_value = mock_user

        mock_cache.get.return_value = "test-uuid"
        mock_cache.ttl.return_value = 3600

        with patch("core.security.JWTHandler.encode", return_value="new_access_token"):
            with patch("core.security.JWTHandler.encode_refresh_token", return_value="new_refresh_token"):
                response = await auth_controller.refresh_token(
                    old_refresh_token="old_refresh_token",
                    session_id="test_session_id",
                    cache=mock_cache,
                )

                assert isinstance(response, Token)
                assert response.access_token == "new_access_token"
                assert response.refresh_token == "new_refresh_token"
                mock_cache.set.assert_called_once()
                mock_cache.delete.assert_called_once_with("old_refresh_token")

    async def test_refresh_token_invalid_token(self, auth_controller, mock_cache):
        """Test refresh token with invalid or missing session ID."""
        mock_cache.get.return_value = None

        with pytest.raises(UnauthorizedException):
            await auth_controller.refresh_token(
                old_refresh_token="invalid_refresh_token",
                session_id="",
                cache=mock_cache,
            )

    async def test_refresh_token_user_not_found(self, auth_controller, mock_user_repository, mock_cache):
        """Test refresh token with user not found."""
        mock_cache.get.return_value = "invalid-uuid"
        mock_user_repository.get_by_uuid.return_value = None

        with pytest.raises(NotFoundException):
            await auth_controller.refresh_token(
                old_refresh_token="valid_refresh_token",
                session_id="test_session_id",
                cache=mock_cache,
            )

    async def test_logout_success(self, auth_controller, mock_cache):
        """Test successful logout."""
        await auth_controller.logout(refresh_token="valid_refresh_token", cache=mock_cache)
        mock_cache.delete.assert_called_once_with("valid_refresh_token")

    async def test_logout_refresh_token_not_found(self, auth_controller):
        """Test logout with missing refresh token."""
        with pytest.raises(NotFoundException):
            await auth_controller.logout(refresh_token="", cache=AsyncMock())
