from fastapi import APIRouter

from .health import health_router

health_check_router = APIRouter()
health_check_router.include_router(health_router, tags=["Health Check"])

__all__ = ["health_router"]
