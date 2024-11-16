from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import HealthCheckController
from core.config import config
from core.db import get_session


def get_health_check(db: AsyncSession = Depends(get_session)) -> HealthCheckController:
    return HealthCheckController(db=db, redis_url=str(config.REDIS_URL))
