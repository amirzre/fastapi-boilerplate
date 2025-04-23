from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import HealthCheckController
from core.config import config
from core.db import get_session


def get_health_check(db: AsyncSession = Depends(get_session)) -> HealthCheckController:
    """
    Retrieve an instance of the HealthCheckController for database and Redis health check.

    This function creates a new `HealthCheckController` with the provided database session
    and the Redis URL from the configuration.

    Args:
        db (AsyncSession): The database session, injected by FastAPI.

    Returns:
        HealthCheckController: The health check controller instance.
    """
    return HealthCheckController(db=db, redis_url=str(config.REDIS_URL))
