from fastapi import status
from redis.asyncio import client

from core.exceptions import CustomException
from core.i18n import translate as _
from core.redis import redis_client


class GetRedisException(CustomException):
    """
    Exception raised when a Redis connection fails.

    Attributes:
        code (int): HTTP status code for internal server error.
        error_code (int): Error code for internal server error.
        message (str): Default error message for Redis connection failure.
    """

    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = _("Redis connection failed.")


async def get_cache() -> client.Redis:
    """
    Retrieve the Redis client after checking its availability.

    This function attempts to ping the Redis server to verify its availability.
    If the server is responsive, the Redis client is returned. Otherwise,
    a `GetRedisException` is raised.

    Returns:
        client.Redis: The Redis client instance.

    Raises:
        GetRedisException: If Redis is not available or the connection fails.
    """
    try:
        if await redis_client.ping():
            return redis_client
    except Exception:
        raise GetRedisException()

    raise GetRedisException()
