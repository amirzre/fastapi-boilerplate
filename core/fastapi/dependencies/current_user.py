from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.controllers import UserController
from app.schemas.response import UserResponse
from core.exceptions import BadRequestException
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationHandler
from core.i18n import translate as _


async def get_authenticated_user(
    request: Request, token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False))
) -> UUID | str:
    """
    Retrieve the authenticated user's UUID from the access token.

    Args:
        request (Request): The current HTTP request.
        token (Optional[HTTPAuthorizationCredentials]): Optional Bearer token from the Authorization header.

    Returns:
        UUID | str: The user's UUID extracted from the token.

    Raises:
        UnauthorizedException: If the token is missing or invalid.
    """
    handler = AuthenticationHandler(request)
    return await handler.authenticate_user(token_type="Access", key="uuid", credentials=token)


async def get_current_user(
    request: Request,
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserResponse:
    """
    Retrieve the current authenticated and active user from the access token.

    Args:
        request (Request): The current HTTP request.
        token (Optional[HTTPAuthorizationCredentials]): Optional Bearer token from the Authorization header.
        user_controller (UserController): Dependency to interact with user data.

    Returns:
        UserResponse: The currently authenticated and active user.

    Raises:
        UnauthorizedException: If the token is missing or invalid.
        BadRequestException: If the user exists but is marked as inactive.
    """
    handler = AuthenticationHandler(request)
    user_uuid = await handler.authenticate_user(token_type="Access", key="uuid", credentials=token)
    user = await user_controller.get_user(user_uuid=UUID(user_uuid))
    if user.activated is False:
        raise BadRequestException(message=_("The user is inactive."))
    return user


async def get_current_user_with_refresh_token(
    request: Request,
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> UUID | str:
    """
    Retrieve the user's UUID from a refresh token for session continuation.

    Args:
        request (Request): The current HTTP request.
        token (Optional[HTTPAuthorizationCredentials]): Optional Bearer token from the Authorization header.

    Returns:
        UUID | str: The user's UUID extracted from the refresh token.

    Raises:
        UnauthorizedException: If the token is missing or invalid.
    """
    handler = AuthenticationHandler(request)
    return await handler.authenticate_user(token_type="Refresh", key="verify", credentials=token)
