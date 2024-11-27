from secrets import token_hex
from unittest.mock import patch

import pytest
from fastapi import FastAPI, Request, status
from starlette.testclient import TestClient

from core.fastapi.middlewares.session import SessionMiddleware


@pytest.mark.asyncio
class TestSessionMiddleware:
    @pytest.fixture
    def mock_app(self):
        """
        Creates a mock FastAPI app with the SessionMiddleware applied.
        """
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(request: Request):
            """
            A sample endpoint to verify middleware behavior.
            """
            return {"session_id": request.cookies.get("Session-Id")}

        app.add_middleware(SessionMiddleware)
        return app

    @pytest.fixture
    def client(self, mock_app):
        """
        Provides a TestClient for the FastAPI app.
        """
        return TestClient(mock_app)

    async def test_no_session_id(self, client):
        """
        Test case where no 'Session-Id' cookie is present in the request.
        """
        response = client.get("/test")

        assert response.status_code == status.HTTP_200_OK
        session_id = response.cookies.get("Session-Id")
        assert session_id is not None
        assert len(session_id) == 32

    async def test_existing_session_id(self, client):
        """
        Test case where an existing 'Session-Id' cookie is provided.
        """
        existing_session_id = token_hex(16)
        client.cookies.set("Session-Id", existing_session_id)
        response = client.get("/test")

        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get("Session-Id") == existing_session_id

    @patch("core.fastapi.middlewares.session.token_hex")
    async def test_generate_new_session_id(self, mock_token_hex, client):
        """
        Test case where the middleware generates a new session ID.
        """
        mock_token_hex.return_value = "mocked_session_id"

        response = client.get("/test")

        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get("Session-Id") == "mocked_session_id"
        mock_token_hex.assert_called_once_with(16)
