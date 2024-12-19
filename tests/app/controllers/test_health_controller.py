from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import HealthCheckController
from app.schemas.response import HealthCheckResponse


@pytest.mark.asyncio
class TestHealthCheckController:
    @pytest.fixture
    def async_session_mock(self):
        """Fixture to provide a mock AsyncSession."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def redis_url(self):
        """Fixture to provide a test Redis URL."""
        return "redis://localhost:6379/0"

    @pytest.fixture
    def health_check_controller(self, async_session_mock, redis_url):
        """Fixture to initialize the HealthCheckController."""
        return HealthCheckController(db=async_session_mock, redis_url=redis_url)

    async def test_check_database_success(self, health_check_controller, async_session_mock):
        """Test that the database check passes when the query executes successfully."""
        async_session_mock.execute.return_value = AsyncMock()

        result = await health_check_controller.check_database()

        assert result is True
        async_session_mock.execute.assert_called_once()

    async def test_check_database_failure(self, health_check_controller, async_session_mock):
        """Test that the database check fails when an exception is raised."""
        async_session_mock.execute.side_effect = Exception("Database unavailable")

        result = await health_check_controller.check_database()

        assert result is False
        async_session_mock.execute.assert_called_once()

    @patch("redis.asyncio.ConnectionPool.from_url")
    @patch("redis.asyncio.Redis")
    async def test_check_redis_success(self, mock_redis, mock_connection_pool, health_check_controller):
        """Test that the Redis check passes when the Redis client can ping."""
        redis_client_mock = AsyncMock()
        mock_redis.return_value = redis_client_mock

        result = await health_check_controller.check_redis()

        assert result is True
        redis_client_mock.ping.assert_called_once()
        redis_client_mock.close.assert_called_once()

    @patch("redis.asyncio.ConnectionPool.from_url")
    @patch("redis.asyncio.Redis")
    async def test_check_redis_failure(self, mock_redis, mock_connection_pool, health_check_controller):
        """Test that the Redis check fails when an exception is raised."""
        mock_redis.side_effect = Exception("Redis unavailable")

        result = await health_check_controller.check_redis()

        assert result is False

    async def test_health_check_all_success(self, health_check_controller, async_session_mock):
        """Test that the health check passes when both database and Redis are healthy."""
        async_session_mock.execute.return_value = AsyncMock()

        with patch.object(health_check_controller, "check_redis", return_value=True) as mock_check_redis:
            response = await health_check_controller.health_check()

        assert isinstance(response, HealthCheckResponse)
        assert response.database is True
        assert response.redis is True
        async_session_mock.execute.assert_called_once()
        mock_check_redis.assert_called_once()

    async def test_health_check_partial_failure(self, health_check_controller, async_session_mock):
        """Test that the health check returns partial success when one service is unavailable."""
        async_session_mock.execute.return_value = AsyncMock()

        with patch.object(health_check_controller, "check_redis", return_value=False) as mock_check_redis:
            response = await health_check_controller.health_check()

        assert isinstance(response, HealthCheckResponse)
        assert response.database is True
        assert response.redis is False
        async_session_mock.execute.assert_called_once()
        mock_check_redis.assert_called_once()

    async def test_health_check_all_failure(self, health_check_controller, async_session_mock):
        """Test that the health check fails when both database and Redis are unavailable."""
        async_session_mock.execute.side_effect = Exception("Database unavailable")

        with patch.object(health_check_controller, "check_redis", return_value=False) as mock_check_redis:
            response = await health_check_controller.health_check()

        assert isinstance(response, HealthCheckResponse)
        assert response.database is False
        assert response.redis is False
        async_session_mock.execute.assert_called_once()
        mock_check_redis.assert_called_once()
