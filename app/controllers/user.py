from pydantic import UUID4

from app.models import User
from app.repositories import UserRepository
from app.schemas.extra import PaginationResponse, UserFilterParams
from app.schemas.request import RegisterUserRequest, UpdateUserRequest
from app.schemas.response import UserResponse
from core.controller import BaseController
from core.db import Transactional
from core.exceptions import BadRequestException, NotFoundException
from core.i18n import translate as _
from core.security import ACLRegistry, PasswordHandler


class UserController(BaseController[User]):
    """
    User controller provides all the logic operations for the User model.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the UserController with the required repository.

        :param user_repository: Repository for handling User model operations.
        """
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    async def get_users(self, *, filter_params: UserFilterParams) -> PaginationResponse[UserResponse]:
        """
        Retrieve users based on the provided filter parameters.

        :param filter_params: Parameters for filtering users (e.g., email, role, activation status, pagination).
        :return: A pagination response containing the filtered users.
        """
        users, total = await self.user_repository.get_filtered_users(filter_params=filter_params)

        return PaginationResponse[UserResponse](
            limit=filter_params.limit, offset=filter_params.offset, total=total, items=users
        )

    async def get_user(self, *, user_uuid: UUID4) -> UserResponse:
        """
        Retrieve a single user by their UUID.

        :param user_uuid: UUID of the user to be retrieved.
        :return: A response object containing the user's details.
        :raises NotFoundException: If the user with the given UUID does not exist.
        """
        user = await self.user_repository.get_by_uuid(uuid=user_uuid)
        if not user:
            raise NotFoundException(message=_("User not found."))

        acl = user.__acl__()
        ACLRegistry.set_acl(resource_id=user.uuid, acl=acl)

        return UserResponse(
            uuid=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            activated=user.activated,
        )

    @Transactional()
    async def register_user(self, *, register_user_request: RegisterUserRequest) -> UserResponse:
        """
        Register a new user in the system.

        :param register_user_request: Request object containing the user's registration details.
        :return: A response object containing details of the newly created user.
        :raises BadRequestException: If a user with the provided email already exists.
        """
        user = await self.user_repository.get_by_email(email=register_user_request.email)
        if user:
            raise BadRequestException(message=_("User already exists with this email."))

        hashed_password = PasswordHandler.hash(password=register_user_request.password)

        user_data = register_user_request.model_dump(exclude_unset=True)
        user_data["password"] = hashed_password
        created_user = await self.user_repository.create(attributes=user_data)
        return UserResponse(
            uuid=created_user.uuid,
            email=created_user.email,
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            role=created_user.role,
            activated=created_user.activated,
        )

    @Transactional()
    async def update_user(self, *, user_uuid: UUID4, update_user_request: UpdateUserRequest) -> UserResponse:
        """
        Update an existing user's details by their UUID.

        :param user_uuid: UUID of the user to be updated.
        :param update_user_request: Request object containing the updated user details.
        :return: A response object containing the updated user's details.
        :raises NotFoundException: If the user with the given UUID does not exist.
        """
        user = await self.user_repository.get_by_uuid(uuid=user_uuid)
        if not user:
            raise NotFoundException(message=_("User not found."))

        update_data = update_user_request.model_dump(exclude_unset=True)
        new_password = update_data.get("password")
        if new_password:
            update_data["password"] = PasswordHandler.hash(password=new_password)

        updated_user = await self.user_repository.update(model=user, attributes=update_data)

        acl = updated_user.__acl__()
        ACLRegistry.set_acl(resource_id=updated_user.uuid, acl=acl)

        return UserResponse(
            uuid=updated_user.uuid,
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            role=updated_user.role,
            activated=updated_user.activated,
        )

    async def delete_user(self, *, user_uuid: UUID4) -> None:
        """
        Delete a user by their UUID.

        :param user_uuid: UUID of the user to be deleted.
        :return: None.
        :raises NotFoundException: If the user with the given UUID does not exist.
        """
        user = await self.user_repository.get_by_uuid(uuid=user_uuid)
        if not user:
            raise NotFoundException(message=_("User not found."))

        acl = user.__acl__()
        ACLRegistry.set_acl(resource_id=user.uuid, acl=acl)

        return await self.user_repository.delete(model=user)
