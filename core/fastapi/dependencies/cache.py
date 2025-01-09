from fastapi import status
from redis.asyncio import client

from core.exceptions import CustomException
from core.i18n import translate as _
from core.redis import redis_client


class GetRedisException(CustomException):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = _("Redis connection failed.")


async def get_cache() -> client.Redis:
    try:
        if await redis_client.ping():
            return redis_client
    except Exception:
        raise GetRedisException()
