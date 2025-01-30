from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Query, status
from pydantic import UUID4

from app.controllers import UserController
from app.models import UserPermission
from app.schemas.extra import PaginationResponse, UserFilterParams
from app.schemas.request import RegisterUserRequest, UpdateUserRequest
from app.schemas.response import UserResponse
from core.cache import Cache
from core.factory import Factory
from core.fastapi.dependencies import IsAdmin, IsAuthenticated, PermissionDependency, Permissions
from core.responses import APIResponse, APIResponseType

user_router = APIRouter()
prefix = "users"


@user_router.get("/", dependencies=[Depends(PermissionDependency([IsAdmin]))])
@Cache.cached(prefix=prefix, ttl=60)
async def get_users(
    filter_params: Annotated[UserFilterParams, Query()],
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> APIResponseType[PaginationResponse[UserResponse]]:
    """
    Retrieve users.
    """
    users = await user_controller.get_users(filter_params=filter_params)
    return APIResponse(users)


@user_router.get("/{user_id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
@Cache.cached(prefix=prefix, ttl=60)
async def get_user(
    user_id: UUID4,
    user_controller: UserController = Depends(Factory().get_user_controller),
    assert_access: Callable = Depends(Permissions(UserPermission.READ)),
) -> APIResponseType[UserResponse]:
    """
    Retrieve user by ID.
    """
    user = await user_controller.get_user(user_uuid=user_id)
    assert_access(resource=user)
    return APIResponse(user)


@user_router.post("/", status_code=status.HTTP_201_CREATED)
@Cache.invalidate_by_prefix(prefix=prefix)
async def register_user(
    register_user_request: RegisterUserRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> APIResponseType[UserResponse]:
    """
    Register new user.
    """
    user = await user_controller.register_user(register_user_request=register_user_request)
    return APIResponse(user)


@user_router.put("/{user_id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
@Cache.invalidate_by_prefix(prefix=prefix)
async def update_user(
    user_id: UUID4,
    update_user_request: UpdateUserRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
    assert_access: Callable = Depends(Permissions(UserPermission.UPDATE)),
) -> APIResponseType[UserResponse]:
    """
    Update a user.
    """
    user = await user_controller.update_user(user_uuid=user_id, update_user_request=update_user_request)
    assert_access(resource=user)
    return APIResponse(user)


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
@Cache.invalidate_by_prefix(prefix=prefix)
async def delete_user(
    user_id: UUID4,
    user_controller: UserController = Depends(Factory().get_user_controller),
    assert_access: Callable = Depends(Permissions(UserPermission.DELETE)),
) -> None:
    """
    Delete a user.
    """
    user = await user_controller.delete_user(user_uuid=user_id)
    assert_access(resource=user)
    return user
