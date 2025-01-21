import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response import HealthCheckResponse
from core.config import config


class HealthCheckController:
    """
    Controller for performing health checks on the system's dependencies, including the database and Redis.
    """

    def __init__(self, db: AsyncSession, redis_url: str) -> None:
        """
        Initialize the HealthCheckController with database and Redis connection details.

        :param db: Asynchronous database session for executing queries.
        :param redis_url: URL of the Redis server for health checks.
        """
        self.db = db
        self.redis_url = redis_url

    async def check_database(self) -> bool:
        """
        Perform a health check on the database.

        Executes a simple query to ensure the database connection is functional.

        :return: True if the database is reachable and the query succeeds; otherwise, False.
        :raises Exception: If an error occurs while executing the database query.
        """
        try:
            await self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def check_redis(self) -> bool:
        """
        Perform a health check on Redis.

        Attempts to ping the Redis server to ensure it is reachable.

        :return: True if the Redis server responds to the ping; otherwise, False.
        :raises Exception: If an error occurs while connecting to or pinging the Redis server.
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
        Perform a health check for all system dependencies.

        Checks the health of both the database and Redis, and returns their status.

        :return: An instance of HealthCheckResponse containing the health status of the database and Redis.
        """
        database = await self.check_database()
        redis = await self.check_redis()
        return HealthCheckResponse(database=database, redis=redis)
