from abc import ABC, abstractmethod
from typing import Type

from fastapi import Request, status
from fastapi.security import APIKeyHeader
from fastapi.security.base import SecurityBase

from app.models import UserRole
from core.exceptions import CustomException
from core.i18n import translate as _


class UnauthorizedException(CustomException):
    """
    Exception raised when a user is not authorized to access a resource.

    Attributes:
        code (int): HTTP status code for unauthorized access.
        error_code (int): Error code for unauthorized access.
        message (str): Default error message for unauthorized access.
    """

    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = _("You are not authorized to access this resource.")


class ForbiddenException(CustomException):
    """
    Exception raised when a user does not have permission to perform an action.

    Attributes:
        code (int): HTTP status code for forbidden access.
        error_code (int): Error code for forbidden access.
        message (str): Default error message for forbidden access.
    """

    code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN
    message = _("You do not have permission to perform this action.")


class BasePermission(ABC):
    """
    Abstract base class for defining custom permissions.

    Subclasses must implement the `has_permission` method to check
    if a request has the required permissions.

    Attributes:
        exception (CustomException): Exception to raise if permission is denied.
    """

    exception = CustomException

    @abstractmethod
    async def has_permission(self, request: Request) -> bool:
        """
        Abstract method to check if a request has the required permissions.

        Args:
            request (Request): The HTTP request to check for permission.

        Returns:
            bool: True if the permission check passes, False otherwise.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        ...


class IsAuthenticated(BasePermission):
    """
    Permission class that checks if the user is authenticated.

    Inherits from `BasePermission`. This class checks if the user is
    authenticated by verifying the presence of a valid UUID in the request state.

    Attributes:
        exception (UnauthorizedException): Exception to raise if the user is not authenticated.
    """

    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        """
        Check if the user is authenticated by verifying if their UUID is present in the request.

        Args:
            request (Request): The HTTP request containing user information in the state.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        user = request.state.user
        return user is not None and user.get("uuid") is not None


class IsAdmin(IsAuthenticated):
    """
    Permission class that checks if the user is an admin.

    Inherits from `IsAuthenticated`. This class checks if the user has
    the `ADMIN` role, in addition to being authenticated.

    Attributes:
        exception (ForbiddenException): Exception to raise if the user is not an admin.
    """

    exception = ForbiddenException

    async def has_permission(self, request: Request) -> bool:
        """
        Check if the user is authenticated and has the admin role.

        Args:
            request (Request): The HTTP request containing user information in the state.

        Returns:
            bool: True if the user is authenticated and has the admin role, False otherwise.
        """
        if not await super().has_permission(request):
            return False

        return request.state.user.get("role") == UserRole.ADMIN


class PermissionDependency(SecurityBase):
    """
    FastAPI dependency for checking multiple permissions on a request.

    This class is used to ensure that a request has all the necessary permissions
    by evaluating a list of permission classes.

    Args:
        permissions (list[Type[BasePermission]]): List of permission classes to check.

    Attributes:
        permissions (list[Type[BasePermission]]): List of permission classes to evaluate.
        model (APIKeyHeader): The security scheme to extract the authorization header.
        scheme_name (str): The name of the security scheme.
    """

    def __init__(self, permissions: list[Type[BasePermission]]):
        self.permissions = permissions
        self.model: APIKeyHeader = APIKeyHeader(name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        """
        Check if the request has all the required permissions.

        Args:
            request (Request): The HTTP request to evaluate for permissions.

        Raises:
            exception: If any of the permission checks fail, the respective exception is raised.
        """
        for permission in self.permissions:
            cls = permission()
            if not await cls.has_permission(request=request):
                raise cls.exception
