from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request, Response, status
from fastapi.testclient import TestClient

from core.fastapi.middlewares.language import LanguageMiddleware


class TestLanguageMiddleware:
    """Test suite for LanguageMiddleware class."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Fixture to create a test FastAPI application with the LanguageMiddleware."""
        app = FastAPI()
        app.add_middleware(LanguageMiddleware)

        @app.get("/test")
        async def test_endpoint() -> dict[str, str]:
            return {"message": "test"}

        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Fixture to create a test client."""
        return TestClient(app)

    async def mock_call_next(self, request: Request) -> Response:
        """Mock function for the call_next parameter in dispatch."""
        return Response(content="Test response", media_type="text/plain")

    def test_middleware_with_language_header(self, client: TestClient) -> None:
        """Test middleware with specific language header."""
        with patch("core.fastapi.middlewares.language.set_locale") as mock_set_locale:
            response = client.get("/test", headers={"Accept-Language": "fa"})

            assert response.status_code == status.HTTP_200_OK
            mock_set_locale.assert_called_once()

    def test_middleware_without_language_header(self, client: TestClient) -> None:
        """
        Test middleware behavior when no language header is present.

        Args:
            client: The test client fixture
        """
        with patch("core.fastapi.middlewares.language.set_locale") as mock_set_locale:
            response = client.get("/test")

            assert response.status_code == status.HTTP_200_OK
            mock_set_locale.assert_called_once()

    def test_middleware_with_multiple_languages(self, client: TestClient) -> None:
        """Test middleware with multiple language preferences in header."""
        with patch("core.fastapi.middlewares.language.set_locale") as mock_set_locale:
            response = client.get("/test", headers={"Accept-Language": "fa,en;q=0.9,es;q=0.8"})

            assert response.status_code == status.HTTP_200_OK
            mock_set_locale.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_preserves_response(self) -> None:
        """Test that middleware preserves the original response from call_next."""
        middleware = LanguageMiddleware(app=Mock())
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [],
                "query_string": b"",
                "client": ("127.0.0.1", 8000),
                "server": ("127.0.0.1", 8000),
                "scheme": "http",
            }
        )

        with patch("core.fastapi.middlewares.language.set_locale"):
            response = await middleware.dispatch(request, self.mock_call_next)

            assert isinstance(response, Response)
            assert response.body == b"Test response"
            assert response.media_type == "text/plain"

    @pytest.mark.asyncio
    async def test_middleware_handles_set_locale_error(self) -> None:
        """Test middleware behavior when set_locale raises an exception."""
        middleware = LanguageMiddleware(app=Mock())
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [],
                "query_string": b"",
                "client": ("127.0.0.1", 8000),
                "server": ("127.0.0.1", 8000),
                "scheme": "http",
            }
        )

        test_error = Exception("Test error")
        with patch("core.fastapi.middlewares.language.set_locale", side_effect=test_error):
            with pytest.raises(Exception) as exc_info:
                await middleware.dispatch(request, self.mock_call_next)
            assert exc_info.value == test_error

    def test_middleware_with_query_param_lang(self, client: TestClient) -> None:
        """Test middleware when language is specified in query parameters."""
        with patch("core.fastapi.middlewares.language.set_locale") as mock_set_locale:
            response = client.get("/test?lang=fa")

            assert response.status_code == status.HTTP_200_OK
            mock_set_locale.assert_called_once()

    def test_middleware_with_cookie_lang(self, client: TestClient) -> None:
        """Test middleware when language is specified in cookies."""
        with patch("core.fastapi.middlewares.language.set_locale") as mock_set_locale:
            client.cookies.set("Accept-Language", "fa")
            response = client.get("/test")

            assert response.status_code == status.HTTP_200_OK
            mock_set_locale.assert_called_once()

            client.cookies.clear()
