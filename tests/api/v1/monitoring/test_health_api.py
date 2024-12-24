import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient

from app.schemas.response import HealthCheckResponse
from core.fastapi.dependencies import get_health_check



@pytest.mark.asyncio
class TestHealthCheckEndpoint:
    @pytest.fixture
    def override_health_check_dependency(self):
        """
        Fixture to mock the HealthCheckController dependency.
        """
        mock_controller = AsyncMock()
        mock_controller.health_check = AsyncMock()
        return mock_controller

    @pytest.fixture(autouse=True)
    def override_dependency(self, app, override_health_check_dependency):
        """
        Override the `get_health_check` dependency globally for all tests in this module.
        """
        app.dependency_overrides[get_health_check] = lambda: override_health_check_dependency

    async def test_health_check_all_services_up(self, client: AsyncClient, override_health_check_dependency):
        """
        Test case where both database and Redis are operational.
        """
        override_health_check_dependency.health_check.return_value = HealthCheckResponse(database=True, redis=True)

        response = await client.get("/api/v1/health/")

        assert response.status_code == 200
        assert response.json() == {"database": True, "redis": True}

    async def test_health_check_database_down(self, client: AsyncClient, override_health_check_dependency):
        """
        Test case where the database is down but Redis is operational.
        """
        override_health_check_dependency.health_check.return_value = HealthCheckResponse(database=False, redis=True)

        response = await client.get("/api/v1/health/")

        assert response.status_code == 200
        assert response.json() == {"database": False, "redis": True}

    async def test_health_check_redis_down(self, client: AsyncClient, override_health_check_dependency):
        """
        Test case where the database is operational but Redis is down.
        """
        override_health_check_dependency.health_check.return_value = HealthCheckResponse(database=True, redis=False)

        response = await client.get("/api/v1/health/")

        assert response.status_code == 200
        assert response.json() == {"database": True, "redis": False}

    async def test_health_check_all_services_down(self, client: AsyncClient, override_health_check_dependency):
        """
        Test case where both database and Redis are down.
        """
        override_health_check_dependency.health_check.return_value = HealthCheckResponse(database=False, redis=False)

        response = await client.get("/api/v1/health/")

        assert response.status_code == 200
        assert response.json() == {"database": False, "redis": False}
