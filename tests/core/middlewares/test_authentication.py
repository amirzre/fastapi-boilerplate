from unittest.mock import patch

import pytest
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from core.exceptions import UnauthorizedException
from core.fastapi.middlewares.authentication import AuthenticationMiddleware


@pytest.mark.asyncio
class TestAuthenticationMiddleware:
    @pytest.fixture
    def mock_app(self):
        """
        Creates a mock FastAPI app with AuthenticationMiddleware and an UnauthorizedException handler.
        """
        app = FastAPI()

        @app.exception_handler(UnauthorizedException)
        async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
            return JSONResponse(status_code=401, content={"detail": str(exc)})

        @app.get("/test")
        async def test_endpoint(request: Request):
            """
            A sample endpoint to verify middleware behavior.
            """
            return {"user": request.state.user}

        app.add_middleware(AuthenticationMiddleware)
        return app

    @pytest.fixture
    def client(self, mock_app):
        """
        Provides a TestClient for the FastAPI app.
        """
        return TestClient(mock_app)

    @patch("core.security.JWTHandler.decode")
    async def test_valid_token(self, mock_decode, client):
        """
        Test case for a valid token.
        """
        mock_decode.return_value = {"uuid": "user-123", "role": "admin"}

        # Set cookie on the TestClient
        client.cookies.set("Access-Token", "valid_token")

        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"user": {"uuid": "user-123", "role": "admin"}}
        mock_decode.assert_called_once_with(token="valid_token")

    async def test_missing_token(self, client):
        """
        Test case where no token is provided in the cookies.
        """
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"user": None}
