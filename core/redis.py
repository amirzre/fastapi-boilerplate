import redis.asyncio as redis

from core.config import config

redis_url = str(config.REDIS_URL)
redis_pool = redis.ConnectionPool.from_url(
    redis_url,
    decode_responses=True,
)
redis_client = redis.Redis(connection_pool=redis_pool)
