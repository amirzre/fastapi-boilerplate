from fastapi import APIRouter, Depends, status
from pydantic import UUID4

from app.controllers import PostController
from app.schemas.request import CreatePostRequest
from app.schemas.response import PostResponse
from core.factory import Factory
from core.responses import APIResponse, APIResponseType

post_router = APIRouter()


@post_router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(
    post_id: UUID4,
    post_controller: PostController = Depends(Factory().get_post_controller),
) -> APIResponseType[PostResponse]:
    """
    Get Post by UUID.
    """
    post = await post_controller.get_post(post_uuid=post_id)
    return APIResponse(post)


@post_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    create_post_request: CreatePostRequest,
    post_controller: PostController = Depends(Factory().get_post_controller),
) -> APIResponseType[PostResponse]:
    """
    Create new post.
    """
    post = await post_controller.create_post(create_post_request=create_post_request)
    return APIResponse(post)
