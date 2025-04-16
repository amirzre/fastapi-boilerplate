from fastapi import Depends, Request, status

from app.controllers.user import UserController
from app.models.user import UserRole
from core.exceptions import CustomException
from core.factory import Factory
from core.i18n import translate as _
from core.security.access_control import AccessControl, Authenticated, Everyone, Principal, RolePrincipal, UserPrincipal


class ForbiddenException(CustomException):
    code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN
    message = _("You do not have permission to perform this action.")


async def get_user_principals(
    request: Request,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> list[Principal]:
    principals: list[Principal] = [Everyone]

    user_uuid = request.state.user.get("uuid")
    if not user_uuid:
        return principals

    user = await user_controller.get_user(user_uuid=user_uuid)

    principals.append(Authenticated)
    principals.append(UserPrincipal(str(user.uuid)))

    if user.role == UserRole.ADMIN:
        principals.append(RolePrincipal(UserRole.ADMIN))

    return principals


Permissions = AccessControl(
    user_principals_getter=get_user_principals,
    permission_exception=ForbiddenException,
)
