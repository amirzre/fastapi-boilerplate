import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response import HealthCheckResponse
from core.config import config


class HealthCheckController:
    def __init__(self, db: AsyncSession, redis_url: str) -> None:
        self.db = db
        self.redis_url = redis_url

    async def check_database(self) -> bool:
        try:
            await self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def check_redis(self) -> bool:
        try:
            redis_pool = redis.ConnectionPool.from_url(str(config.REDIS_URL), decode_responses=True)
            redis_client = redis.Redis(connection_pool=redis_pool)
            await redis_client.ping()
            await redis_client.close()
            return True
        except Exception:
            return False

    async def health_check(self) -> HealthCheckResponse:
        database = await self.check_database()
        redis = await self.check_redis()
        return HealthCheckResponse(database=database, redis=redis)
