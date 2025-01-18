from fastapi import APIRouter

from .posts import post_router

posts_router = APIRouter()
posts_router.include_router(post_router, tags=["Posts"])

__all__ = ["posts_router"]
