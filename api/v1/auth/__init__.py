from fastapi import APIRouter

from .auth import auth_router

auth_routers = APIRouter()
auth_routers.include_router(auth_router, tags=["Auth"])

__all__ = ["auth_routers"]
