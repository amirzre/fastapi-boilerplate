from fastapi import Depends, Request, status

from app.controllers.user import UserController
from app.models.user import UserRole
from core.exceptions import CustomException
from core.factory import Factory
from core.i18n import translate as _
from core.security.access_control import AccessControl, Authenticated, Everyone, Principal, RolePrincipal, UserPrincipal


class ForbiddenException(CustomException):
    """
    Exception raised when a user attempts an action they are not authorized to perform.

    Attributes:
        code (int): HTTP status code returned by the exception.
        error_code (int): Application-specific error code.
        message (str): Description of the error message, localized if necessary.
    """

    code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN
    message = _("You do not have permission to perform this action.")


async def get_user_principals(
    request: Request,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> list[Principal]:
    """
    Retrieve a list of security principals associated with the current user.

    Principals represent different levels of access or identity, including:
    - `Everyone`: A generic principal for all users.
    - `Authenticated`: A principal for logged-in users.
    - `UserPrincipal`: A specific principal tied to the user's UUID.
    - `RolePrincipal`: A role-based principal, e.g., admin access.

    Args:
        request (Request): The current request object, used to retrieve user session information.
        user_controller (UserController): Dependency to retrieve user information.

    Returns:
        list[Principal]: A list of principals for permission evaluation.
    """
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
"""
Access control instance configured with the user principal retrieval function and a custom
exception to raise when permission is denied.

Used to enforce resource access rules throughout the application.
"""
