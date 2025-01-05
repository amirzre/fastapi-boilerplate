from abc import ABC, abstractmethod
from typing import Type

from fastapi import Request, status
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.models import UserRole
from core.exceptions import CustomException


class UnauthorizedException(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = "You are not authorized to access this resource."


class ForbiddenException(CustomException):
    code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN
    message = "You do not have permission to perform this action."


class BasePermission(ABC):
    exception = CustomException

    @abstractmethod
    async def has_permission(self, request: Request) -> bool:
        """has permssion"""


class IsAuthenticated(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        user = request.state.user
        return user is not None and user.get("uuid") is not None


class IsAdmin(IsAuthenticated):
    exception = ForbiddenException

    async def has_permission(self, request: Request) -> bool:
        if not await super().has_permission(request):
            return False

        return request.state.user.get("role") == UserRole.ADMIN


class PermissionDependency(SecurityBase):
    def __init__(self, permissions: list[Type[BasePermission]]):
        self.permissions = permissions
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        for permission in self.permissions:
            cls = permission()
            if not await cls.has_permission(request=request):
                raise cls.exception
