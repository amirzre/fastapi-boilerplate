import asyncio
import secrets

from redis.asyncio import client

from app.models import User
from app.repositories import UserRepository
from app.schemas.extra import Token
from app.schemas.request import UserLoginRequest
from core.controller import BaseController
from core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from core.i18n import translate as _
from core.security import JWTHandler, PasswordHandler


class AuthController(BaseController[User]):
    """
    Auth controller provides all the logic operations for the user authentication.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the AuthController with the required repository.

        :param user_repository: Repository for handling User model operations.
        """
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    async def login(self, *, login_user_request: UserLoginRequest, cache: client.Redis) -> Token:
        """
        Authenticate a user and generate access, refresh, and CSRF tokens.

        :param login_user_request: Request object containing the user's email and password.
        :param cache: Redis client for storing the refresh token.
        :return: A Token object containing access, refresh, and CSRF tokens.
        :raises BadRequestException: If the user's credentials are invalid or the user is inactive.
        """
        user = await self.user_repository.get_by_email(email=login_user_request.email)
        if not user:
            raise BadRequestException(message=_("Invalid credentials."))
        if not PasswordHandler.verify(plain_password=login_user_request.password, hashed_password=user.password):
            raise BadRequestException(message=_("Invalid credentials."))
        if user.activated is False:
            raise BadRequestException(message=_("The user is inactive."))

        refresh_token = JWTHandler.encode_refresh_token(
            payload={"sub": "refresh_token", "verify": str(user.uuid), "role": user.role}
        )
        access_token = JWTHandler.encode(payload={"uuid": str(user.uuid), "role": user.role})
        csrf_token = secrets.token_hex(32)

        await cache.set(name=refresh_token, value=str(user.uuid), ex=JWTHandler.refresh_token_expire)

        return Token(access_token=access_token, refresh_token=refresh_token, csrf_token=csrf_token)

    async def refresh_token(self, *, old_refresh_token: str, session_id: str, cache: client.Redis) -> Token:
        """
        Generate a new access token and refresh token using an existing refresh token.

        :param old_refresh_token: The existing refresh token to be refreshed.
        :param session_id: The session identifier associated with the user.
        :param cache: Redis client for managing tokens.
        :return: A Token object containing new access, refresh, and CSRF tokens.
        :raises UnauthorizedException: If the refresh token or session ID is invalid.
        :raises NotFoundException: If the user associated with the refresh token is not found.
        """
        uuid, ttl = await asyncio.gather(cache.get(old_refresh_token), cache.ttl(old_refresh_token))
        if not uuid or not session_id:
            raise UnauthorizedException(message=_("Invalid token or missing session ID."))

        user = await self.user_repository.get_by_uuid(uuid=uuid)
        if not user:
            raise NotFoundException(message=_("User not found."))

        access_token = JWTHandler.encode(payload={"uuid": str(uuid), "role": user.role})
        refresh_token = JWTHandler.encode_refresh_token(
            payload={"sub": "refresh_token", "verify": str(uuid), "role": user.role}
        )
        csrf_token = secrets.token_hex(32)

        await asyncio.gather(cache.set(name=refresh_token, value=uuid, ex=ttl), cache.delete(old_refresh_token))

        return Token(access_token=access_token, refresh_token=refresh_token, csrf_token=csrf_token)

    async def logout(self, *, refresh_token: str, cache: client.Redis) -> None:
        """
        Log out a user by deleting their refresh token from the cache.

        :param refresh_token: The refresh token to be deleted.
        :param cache: Redis client for managing tokens.
        :return: None.
        :raises NotFoundException: If the refresh token is not provided.
        """
        if not refresh_token:
            raise NotFoundException(message=_("Refresh token not found."))
        await cache.delete(refresh_token)
        return None
