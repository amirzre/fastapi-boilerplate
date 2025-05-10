import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response import HealthCheckResponse
from core.config import config


class HealthCheckController:
    """
    Controller responsible for performing health checks on core system dependencies,
    including the database and Redis.
    """

    def __init__(self, db: AsyncSession, redis_url: str) -> None:
        """
        Initialize the HealthCheckController.

        Args:
            db (AsyncSession): SQLAlchemy asynchronous database session.
            redis_url (str): Connection URL for the Redis server.
        """
        self.db = db
        self.redis_url = redis_url

    async def check_database(self) -> bool:
        """
        Check the availability of the database.

        Executes a lightweight query to verify that the database connection is alive.

        Returns:
            bool: True if the database responds correctly; False otherwise.
        """
        try:
            await self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def check_redis(self) -> bool:
        """
        Check the availability of the Redis server.

        Uses a ping command to confirm that the Redis server is reachable.

        Returns:
            bool: True if Redis is reachable and responds to ping; False otherwise.
        """
        try:
            redis_pool = redis.ConnectionPool.from_url(str(config.REDIS_URL), decode_responses=True)
            redis_client = redis.Redis(connection_pool=redis_pool)
            await redis_client.ping()
            await redis_client.close()
            return True
        except Exception:
            return False

    async def health_check(self) -> HealthCheckResponse:
        """
        Run health checks for all major dependencies.

        Returns:
            HealthCheckResponse: Object containing the health status of the database and Redis.
        """
        database = await self.check_database()
        redis = await self.check_redis()
        return HealthCheckResponse(database=database, redis=redis)
