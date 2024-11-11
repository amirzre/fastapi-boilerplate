from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.controllers import UserController
from app.schemas.extra import PaginationResponse, UserFilterParams
from app.schemas.request import RegisterUserRequest, UpdateUserRequest
from app.schemas.response import UserResponse
from core.cache import Cache
from core.factory import Factory
from core.fastapi.dependencies import IsAdmin, IsAuthenticated, PermissionDependency

user_router = APIRouter()
prefix = "users"


@user_router.get("/", dependencies=[Depends(PermissionDependency([IsAdmin]))])
@Cache.cached(prefix=prefix, ttl=60)
async def get_users(
    filter_params: Annotated[UserFilterParams, Query()],
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> PaginationResponse[UserResponse]:
    """
    Retrieve users.
    """
    return await user_controller.get_filtered_user(filter_params=filter_params)


@user_router.get("/{id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
@Cache.cached(prefix=prefix, ttl=60)
async def get_user(id=UUID, user_controller: UserController = Depends(Factory().get_user_controller)) -> UserResponse:
    """
    Retrieve user by ID.
    """
    return await user_controller.get_user(user_uuid=id)


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(
    register_user_request: RegisterUserRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserResponse:
    """
    Register new user.
    """
    await Cache.remove_by_prefix(prefix=prefix)
    return await user_controller.register_user(register_user_request=register_user_request)


@user_router.put("/{id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def update_user(
    id: UUID,
    update_user_request: UpdateUserRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserResponse:
    """
    Update a user.
    """
    await Cache.remove_by_prefix(prefix=prefix)
    return await user_controller.update_user(user_uuid=id, update_user_request=update_user_request)


@user_router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
async def delete_user(
    id: UUID,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> None:
    """
    Delete a user.
    """
    await Cache.remove_by_prefix(prefix=prefix)
    return await user_controller.delete_user(user_uuid=id)
