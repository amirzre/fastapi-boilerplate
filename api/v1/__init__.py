from fastapi import APIRouter

from .auth import auth_routers
from .monitoring import health_check_router
from .users import users_router

v1_router = APIRouter()
v1_router.include_router(auth_routers, prefix="/auth")
v1_router.include_router(users_router, prefix="/users")
v1_router.include_router(health_check_router, prefix="/health")
