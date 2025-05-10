from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials

from core.exceptions import UnauthorizedException
from core.fastapi.dependencies import AuthenticationHandler
from core.security import JWTHandler


@pytest.mark.asyncio
class TestAuthenticationHandler:
    @pytest.fixture
    def mock_request(self):
        """Fixture to create a mocked FastAPI Request object."""
        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {}
        return mock_request

    @pytest.fixture
    def mock_jwt_handler(self, monkeypatch):
        """Fixture to mock the JWTHandler.decode method."""
        decode_mock = MagicMock(return_value={"uuid": "test-uuid"})
        monkeypatch.setattr(JWTHandler, "decode", decode_mock)
        return decode_mock

    @pytest.fixture
    def auth_handler(self, mock_request):
        """Fixture to initialize AuthenticationHandler with a mocked request."""
        return AuthenticationHandler(mock_request)

    async def test_get_token_success(self, auth_handler, mock_request):
        """Test successful retrieval of a token from cookies."""
        mock_request.cookies = {"Access-Token": "test-token"}
        token = await auth_handler._get_token("Access")
        assert token == "test-token"

    async def test_get_token_failure(self, auth_handler):
        """Test retrieval of a token when the token is missing."""
        with pytest.raises(UnauthorizedException):
            await auth_handler._get_token("Access")

    async def test_decode_token_success(self, auth_handler, mock_jwt_handler):
        """Test decoding a valid token."""
        decoded_uuid = await auth_handler._decode_token("valid-token", "uuid")
        assert decoded_uuid == "test-uuid"
        mock_jwt_handler.assert_called_once_with(token="valid-token")

    async def test_validate_token_success(self, auth_handler):
        """Test successful validation of a token."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        await auth_handler._validate_token("test-token", credentials, "Access")

    async def test_validate_token_failure_scheme(self, auth_handler):
        """Test token validation failure due to incorrect scheme."""
        credentials = HTTPAuthorizationCredentials(scheme="Invalid", credentials="test-token")
        with pytest.raises(UnauthorizedException):
            await auth_handler._validate_token("test-token", credentials, "Access")

    async def test_validate_token_failure_credentials(self, auth_handler):
        """Test token validation failure due to mismatched credentials."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-token")
        with pytest.raises(UnauthorizedException):
            await auth_handler._validate_token("test-token", credentials, "Access")

    async def test_authenticate_user_success(self, auth_handler, mock_jwt_handler):
        """Test the full authentication flow."""
        auth_handler.request.cookies = {"Access-Token": "test-token"}
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        user_uuid = await auth_handler.authenticate_user("Access", "uuid", credentials)
        assert user_uuid == "test-uuid"
        mock_jwt_handler.assert_called_once_with(token="test-token")

    async def test_authenticate_user_missing_token(self, auth_handler):
        """Test the authentication flow when the token is missing."""
        with pytest.raises(UnauthorizedException):
            await auth_handler.authenticate_user("Access", "uuid")
