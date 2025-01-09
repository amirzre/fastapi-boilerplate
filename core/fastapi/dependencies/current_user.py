from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.controllers import UserController
from app.models import User
from core.exceptions import BadRequestException
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationHandler
from core.i18n import translate as _


async def get_authenticated_user(
    request: Request, token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False))
) -> UUID | str:
    handler = AuthenticationHandler(request)
    return await handler.authenticate_user(token_type="Access", key="uuid", credentials=token)


async def get_current_user(
    request: Request,
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> User:
    handler = AuthenticationHandler(request)
    user_uuid = await handler.authenticate_user(token_type="Access", key="uuid", credentials=token)
    user = await user_controller.get_by_uuid(uuid=user_uuid)
    if user.activated is False:
        raise BadRequestException(message=_("The user is inactive."))
    return user


async def get_current_user_with_refresh_token(
    request: Request,
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> UUID | str:
    handler = AuthenticationHandler(request)
    return await handler.authenticate_user(token_type="Refresh", key="verify", credentials=token)
