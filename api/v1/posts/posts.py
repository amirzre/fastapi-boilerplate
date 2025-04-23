from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Query, status
from pydantic import UUID4

from app.controllers import PostController
from app.models import PostPermission
from app.schemas.extra import PaginationResponse
from app.schemas.request import CreatePostRequest, PostFilterParams, UpdatePostRequest
from app.schemas.response import PostResponse
from core.factory import Factory
from core.fastapi.dependencies import IsAuthenticated, PermissionDependency, Permissions
from core.responses import APIResponse, APIResponseType

post_router = APIRouter()


@post_router.get(
    "/{user_id}/posts",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    status_code=status.HTTP_200_OK,
)
async def get_user_posts(
    user_id: UUID4,
    filter_params: Annotated[PostFilterParams, Query()],
    post_controller: PostController = Depends(Factory().get_post_controller),
    assert_access: Callable = Depends(Permissions(PostPermission.READ)),
) -> APIResponseType[PaginationResponse[PostResponse]]:
    """
    Retrieve a paginated list of posts created by a specific user.

    - **user_id**: `UUID` of the user whose posts are to be fetched.
    - **filter_params**: Optional query parameters for filtering and pagination.
    - **Permissions**: Requires `authentication` and `read` access to the resource.
    """
    posts = await post_controller.get_user_posts(user_id=user_id, filter_params=filter_params)
    assert_access(resource=posts)
    return APIResponse(posts)


@post_router.get(
    "/{post_id}",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    status_code=status.HTTP_200_OK,
)
async def get_post(
    post_id: UUID4,
    post_controller: PostController = Depends(Factory().get_post_controller),
    assert_access: Callable = Depends(Permissions(PostPermission.READ)),
) -> APIResponseType[PostResponse]:
    """
    Retrieve a single post by its UUID.

    - **post_id**: `UUID` of the post to retrieve.
    - **Permissions**: Requires `authentication` and `read` access to the post.
    """
    post = await post_controller.get_post(post_uuid=post_id)
    assert_access(resource=post)
    return APIResponse(post)


@post_router.post(
    "/",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    create_post_request: CreatePostRequest,
    post_controller: PostController = Depends(Factory().get_post_controller),
    assert_access: Callable = Depends(Permissions(PostPermission.CREATE)),
) -> APIResponseType[PostResponse]:
    """
    Create a new post.

    - **create_post_request**: Request body containing post data (title, content, etc.).
    - **Permissions**: Requires `authentication` and `create` permission.
    """
    post = await post_controller.create_post(create_post_request=create_post_request)
    assert_access(resource=post)
    return APIResponse(post)


@post_router.put(
    "/{post_id}",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    status_code=status.HTTP_200_OK,
)
async def update_post(
    post_id: UUID4,
    update_post_request: UpdatePostRequest,
    post_controller: PostController = Depends(Factory().get_post_controller),
    assert_access: Callable = Depends(Permissions(PostPermission.UPDATE)),
) -> APIResponseType[PostResponse]:
    """
    Update an existing post by its UUID.

    - **post_id**: `UUID` of the post to update.
    - **update_post_request**: Request body with updated post data.
    - **Permissions**: Requires `authentication` and `update` permission.
    """
    post = await post_controller.update_post(post_uuid=post_id, update_post_request=update_post_request)
    assert_access(resource=post)
    return APIResponse(post)


@post_router.delete(
    "/{post_id}",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: UUID4,
    post_controller: PostController = Depends(Factory().get_post_controller),
    assert_access: Callable = Depends(Permissions(PostPermission.DELETE)),
) -> None:
    """
    Delete a post by its UUID.

    - **post_id**: `UUID` of the post to delete.
    - **Permissions**: Requires `authentication` and `delete` permission.
    """
    post = await post_controller.delete_post(post_uuid=post_id)
    assert_access(resource=post)
    return None
