from fastapi import APIRouter, Depends

from app.controllers import HealthCheckController
from app.schemas.response import HealthCheckResponse
from core.fastapi.dependencies import get_health_check

health_router = APIRouter()


@health_router.get("/")
async def health_check(
    health_check_controller: HealthCheckController = Depends(get_health_check),
) -> HealthCheckResponse:
    """
    Return database, cache and etc status.
    """
    return await health_check_controller.health_check()
