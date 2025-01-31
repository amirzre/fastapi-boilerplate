import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request

from app.controllers.user import UserController
from app.models.user import UserRole
from core.factory import Factory
from core.fastapi.dependencies.acl import ForbiddenException, Permissions, get_user_principals
from core.security.access_control import Authenticated, Everyone, RolePrincipal, UserPrincipal


class TestForbiddenException:
    """
    Test suite for ForbiddenException class.
    Verifies the exception's attributes and behavior.
    """

    def test_forbidden_exception_attributes(self):
        """Test that ForbiddenException has the correct attributes and values."""
        exception = ForbiddenException()
        assert exception.code == 403
        assert exception.error_code == 403
        assert "permission" in str(exception.message).lower()


class TestGetUserPrincipals:
    """
    Test suite for get_user_principals function.
    Tests various scenarios of user authentication and role-based permissions.
    """

    @pytest.fixture
    def mock_request(self):
        """Fixture to create a mock FastAPI request."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        return request

    @pytest.fixture
    def mock_user_controller(self):
        """Fixture to create a mock UserController."""
        return AsyncMock(spec=UserController)

    @pytest.fixture
    def mock_factory(self):
        """Fixture to create a mock Factory that returns the mock UserController."""
        factory = MagicMock(spec=Factory)
        factory.get_user_controller = MagicMock(return_value=AsyncMock(spec=UserController))
        return factory

    @pytest.mark.asyncio
    async def test_get_principals_no_user(self, mock_request, mock_user_controller):
        """
        Test getting principals when no user is authenticated.
        Should return only Everyone principal.
        """
        mock_request.state.user = {"uuid": None}

        principals = await get_user_principals(request=mock_request, user_controller=mock_user_controller)

        assert principals == [Everyone]
        mock_user_controller.get_by_uuid.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_principals_regular_user(self, mock_request, mock_user_controller):
        """
        Test getting principals for a regular authenticated user.
        Should return Everyone, Authenticated, and UserPrincipal.
        """
        user_id = uuid.uuid4()
        mock_request.state.user = {"uuid": user_id}

        mock_user = AsyncMock()
        mock_user.uuid = user_id
        mock_user.role = UserRole.USER
        mock_user_controller.get_by_uuid.return_value = mock_user

        principals = await get_user_principals(request=mock_request, user_controller=mock_user_controller)

        assert Everyone in principals
        assert Authenticated in principals
        assert UserPrincipal(str(user_id)) in principals
        assert RolePrincipal(UserRole.ADMIN) not in principals
        mock_user_controller.get_by_uuid.assert_called_once_with(uuid=user_id)

    @pytest.mark.asyncio
    async def test_get_principals_admin_user(self, mock_request, mock_user_controller):
        """
        Test getting principals for an admin user.
        Should return Everyone, Authenticated, UserPrincipal, and AdminRole.
        """
        user_id = uuid.uuid4()
        mock_request.state.user = {"uuid": user_id}

        mock_user = AsyncMock()
        mock_user.uuid = user_id
        mock_user.role = UserRole.ADMIN
        mock_user_controller.get_by_uuid.return_value = mock_user

        principals = await get_user_principals(request=mock_request, user_controller=mock_user_controller)

        assert Everyone in principals
        assert Authenticated in principals
        assert UserPrincipal(str(user_id)) in principals
        assert RolePrincipal(UserRole.ADMIN) in principals
        mock_user_controller.get_by_uuid.assert_called_once_with(uuid=user_id)


class TestPermissionsIntegration:
    """
    Integration test suite for Permissions system.
    Tests the complete flow from request to permission checking.
    """

    @pytest.fixture
    def mock_request(self):
        """Fixture to create a mock FastAPI request with user state."""
        request = MagicMock(spec=Request)
        request.state.user = {"uuid": uuid.uuid4()}
        return request

    @pytest.fixture
    def mock_user_controller(self):
        """Fixture to create a mock UserController with user data."""
        controller = AsyncMock(spec=UserController)
        mock_user = AsyncMock()
        mock_user.uuid = uuid.uuid4()
        mock_user.role = UserRole.USER
        controller.get_by_uuid.return_value = mock_user
        return controller

    @pytest.mark.asyncio
    async def test_complete_permission_flow(self, mock_request, mock_user_controller):
        """
        Test the complete flow of permission checking from request to access control.
        Verifies that all components work together correctly.
        """
        permission_name = "test_permission"

        # Create a test endpoint with Permissions
        @Permissions(permission_name)
        async def test_endpoint(request: Request = mock_request):
            return {"message": "success"}

        # Mock the necessary components
        with patch("core.fastapi.dependencies.acl.get_user_principals") as mock_get_principals:
            mock_get_principals.return_value = [Everyone, Authenticated]

            with patch("core.security.access_control.AccessControl.assert_access") as mock_assert:
                mock_assert.side_effect = ForbiddenException()
                with pytest.raises(ForbiddenException) as exc_info:
                    await test_endpoint(resource="test_resource")
