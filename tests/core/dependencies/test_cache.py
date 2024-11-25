from unittest.mock import AsyncMock, patch

import pytest

from core.fastapi.dependencies.cache import GetRedisException, get_cache


@pytest.mark.asyncio
class TestGetCache:
    @patch("core.fastapi.dependencies.cache.redis_client", new_callable=AsyncMock)
    async def test_get_cache_success(self, mock_redis_client):
        """Test that cache connected successfully."""
        mock_redis_client.ping.return_value = True

        result = await get_cache()
        assert result is mock_redis_client
        mock_redis_client.ping.assert_called_once()

    @patch("core.fastapi.dependencies.cache.redis_client", new_callable=AsyncMock)
    async def test_get_cache_failure(self, mock_redis_client):
        """Test that cache not connected successfully."""
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")

        with pytest.raises(GetRedisException):
            await get_cache()
        mock_redis_client.ping.assert_called_once()
