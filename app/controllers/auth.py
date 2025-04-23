import asyncio
import secrets

from redis.asyncio import client

from app.models import User
from app.repositories import UserRepository
from app.schemas.request import UserLoginRequest
from app.schemas.response import TokenResponse
from core.controller import BaseController
from core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from core.i18n import translate as _
from core.security import JWTHandler, PasswordHandler


class AuthController(BaseController[User]):
    """
    Controller responsible for handling user authentication processes,
    including login, token refresh, and logout operations.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the AuthController with the specified user repository.

        Args:
            user_repository (UserRepository): Repository instance for user data operations.
        """
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    async def login(self, *, login_user_request: UserLoginRequest, cache: client.Redis) -> TokenResponse:
        """
        Authenticate a user using provided credentials and issue authentication tokens.

        Args:
            login_user_request (UserLoginRequest): Object containing user's email and password.
            cache (client.Redis): Redis client instance for token storage.

        Returns:
            TokenResponse: Object containing access token, refresh token, and CSRF token.

        Raises:
            BadRequestException: If credentials are invalid or user is inactive.
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

        return TokenResponse(access_token=access_token, refresh_token=refresh_token, csrf_token=csrf_token)

    async def refresh_token(self, *, old_refresh_token: str, session_id: str, cache: client.Redis) -> TokenResponse:
        """
        Refresh authentication tokens using an existing refresh token and session ID.

        Args:
            old_refresh_token (str): The existing refresh token to be replaced.
            session_id (str): Identifier for the user's session.
            cache (client.Redis): Redis client instance for token management.

        Returns:
            TokenResponse: Object containing new access token, refresh token, and CSRF token.

        Raises:
            UnauthorizedException: If the refresh token or session ID is invalid.
            NotFoundException: If the user associated with the token is not found.
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

        return TokenResponse(access_token=access_token, refresh_token=refresh_token, csrf_token=csrf_token)

    async def logout(self, *, refresh_token: str, cache: client.Redis) -> None:
        """
        Log out a user by removing their refresh token from the cache.

        Args:
            refresh_token (str): The refresh token to be invalidated.
            cache (client.Redis): Redis client instance for token management.

        Raises:
            NotFoundException: If the refresh token is not provided.
        """
        if not refresh_token:
            raise NotFoundException(message=_("Refresh token not found."))
        await cache.delete(refresh_token)

        return None
