from uuid import UUID

from app.models import User
from app.repositories import UserRepository
from app.schemas.extra import PaginationResponse, UserFilterParams
from app.schemas.request import RegisterUserRequest, UpdateUserRequest
from app.schemas.response import UserResponse
from core.controller import BaseController
from core.db import Transactional
from core.exceptions import BadRequestException, NotFoundException
from core.security import PasswordHandler


class UserController(BaseController[User]):
    """
    User controller provides all the logic operations for the User model.
    """

    def __init__(self, user_repository: UserRepository):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    async def get_filtered_user(self, *, filter_params: UserFilterParams) -> PaginationResponse[UserResponse]:
        users, total = await self.user_repository.get_filtered_users(filter_params=filter_params)
        return PaginationResponse[UserResponse](
            limit=filter_params.limit, offset=filter_params.offset, total=total, items=users
        )

    async def get_user(self, *, user_uuid: UUID) -> User:
        user = await self.user_repository.get_by_uuid(uuid=user_uuid)
        if not user:
            raise NotFoundException(message="User not found.")
        return user

    @Transactional()
    async def register_user(self, *, register_user_request: RegisterUserRequest) -> User:
        user = await self.user_repository.get_by_email(email=register_user_request.email)
        if user:
            raise BadRequestException(message="User already exists with this email.")

        hashed_password = PasswordHandler.hash(password=register_user_request.password)

        user_data = register_user_request.model_dump(exclude_unset=True)
        user_data["password"] = hashed_password
        return await self.user_repository.create(attributes=user_data)

    @Transactional()
    async def update_user(self, *, user_uuid: UUID, update_user_request: UpdateUserRequest) -> User:
        user = await self.user_repository.get_by_uuid(uuid=user_uuid)
        if not user:
            raise NotFoundException(message="User not found.")

        update_data = update_user_request.model_dump(exclude_unset=True)
        new_password = update_data.get("password")
        if new_password:
            update_data["password"] = PasswordHandler.hash(password=new_password)

        return await self.user_repository.update(model=user, attributes=update_data)

    async def delete_user(self, *, user_uuid: UUID) -> None:
        user = await self.user_repository.get_by_uuid(uuid=user_uuid)
        if not user:
            raise NotFoundException(message="User not found.")

        return await self.user_repository.delete(model=user)
