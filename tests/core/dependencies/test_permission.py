from unittest.mock import MagicMock

import pytest

from app.models import UserRole
from core.fastapi.dependencies.permission import (
    ForbiddenException,
    IsAdmin,
    IsAuthenticated,
    PermissionDependency,
    UnauthorizedException,
)


@pytest.mark.asyncio
class TestPermissions:
    async def test_is_authenticated_success(self):
        """Test that `IsAuthenticated` permission allows access when the request contains a valid user with a `uuid`."""
        request = MagicMock()
        request.state.user = {"uuid": "test-uuid"}

        permission = IsAuthenticated()
        assert await permission.has_permission(request)

    async def test_is_authenticated_fail_no_user(self):
        """Test that `IsAuthenticated` permission denies access when the request contains no user."""
        request = MagicMock()
        request.state.user = None

        permission = IsAuthenticated()
        assert not await permission.has_permission(request)

    async def test_is_authenticated_fail_no_uuid(self):
        """Test that `IsAuthenticated` permission denies access when the user object does not contain a `uuid`."""
        request = MagicMock()
        request.state.user = {"role": UserRole.USER}

        permission = IsAuthenticated()
        assert not await permission.has_permission(request)

    async def test_is_admin_success(self):
        """Test that `IsAdmin` permission allows access when the request contains a valid admin user."""
        request = MagicMock()
        request.state.user = {"uuid": "test-uuid", "role": UserRole.ADMIN}

        permission = IsAdmin()
        assert await permission.has_permission(request)

    async def test_is_admin_fail_not_authenticated(self):
        """Test that `IsAdmin` permission denies access when the request contains no user."""
        request = MagicMock()
        request.state.user = None

        permission = IsAdmin()
        assert not await permission.has_permission(request)

    async def test_is_admin_fail_not_admin(self):
        """Test that `IsAdmin` permission denies access when the user is not an admin."""
        request = MagicMock()
        request.state.user = {"uuid": "test-uuid", "role": UserRole.USER}

        permission = IsAdmin()
        assert not await permission.has_permission(request)

    async def test_permission_dependency_success(self):
        """Test that `PermissionDependency` allows access when all the provided permissions are satisfied."""
        request = MagicMock()
        request.state.user = {"uuid": "test-uuid", "role": UserRole.ADMIN}

        dependency = PermissionDependency(permissions=[IsAuthenticated, IsAdmin])
        await dependency(request)

    async def test_permission_dependency_fail(self):
        """Test that `PermissionDependency` denies access when one of the permissions fails."""
        request = MagicMock()
        request.state.user = {"uuid": "test-uuid", "role": UserRole.USER}

        dependency = PermissionDependency(permissions=[IsAuthenticated, IsAdmin])

        with pytest.raises(ForbiddenException):
            await dependency(request)

    async def test_permission_dependency_unauthorized(self):
        """Test that `PermissionDependency` denies access when the user is not authenticated."""
        request = MagicMock()
        request.state.user = None

        dependency = PermissionDependency(permissions=[IsAuthenticated])

        with pytest.raises(UnauthorizedException):
            await dependency(request)
