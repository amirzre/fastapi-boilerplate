from dataclasses import dataclass
from typing import cast
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import UUID4

from core.security.access_control import (
    AccessControl,
    ACLList,
    ACLRegistry,
    Allow,
    AllowAll,
    Deny,
    Everyone,
    Principal,
    RolePrincipal,
    SystemPrincipal,
    UserPrincipal,
)


@dataclass
class MockResource:
    """Mock resource class for testing ACL functionality."""

    uuid: UUID4 = uuid4()

    @property
    def __acl__(self) -> list[tuple[str, Principal, list[str]]]:
        return [
            (Allow, Everyone, ["view"]),
            (Allow, UserPrincipal("user1"), ["edit", "delete"]),
            (Deny, UserPrincipal("banned_user"), ["view", "edit", "delete"]),
        ]


class TestPrincipalClasses:
    """
    Test suite for various Principal class implementations.
    Tests the creation and string representation of different principal types.
    """

    def test_principal_creation(self) -> None:
        """Test basic Principal class creation and representation."""
        principal = Principal(key="test", value="value")
        assert str(principal) == "test:value"
        assert repr(principal) == "test:value"

    def test_system_principal(self) -> None:
        """Test SystemPrincipal creation and key assignment."""
        sys_principal = SystemPrincipal(value="sys_user")
        assert sys_principal.key == "system"
        assert sys_principal.value == "sys_user"

    def test_user_principal(self) -> None:
        """Test UserPrincipal creation and key assignment."""
        user_principal = UserPrincipal(value="john_doe")
        assert user_principal.key == "user"
        assert user_principal.value == "john_doe"

    def test_role_principal(self) -> None:
        """Test RolePrincipal creation and key assignment."""
        role_principal = RolePrincipal(value="admin")
        assert role_principal.key == "role"
        assert role_principal.value == "admin"


class TestACLRegistry:
    """
    Test suite for ACLRegistry functionality.
    Tests the storage and retrieval of ACL rules for resources.
    """

    def setup_method(self) -> None:
        """Reset the ACL registry before each test."""
        ACLRegistry._acl_map = {}

    def test_set_and_get_acl(self) -> None:
        """Test setting and retrieving ACL rules for a resource."""
        resource_id = uuid4()
        acl_rules = cast(ACLList, [(Allow, UserPrincipal("user1"), ["read"])])

        ACLRegistry.set_acl(resource_id, acl_rules)

        retrieved_acl = ACLRegistry.get_acl(resource_id)

        assert retrieved_acl == acl_rules

    def test_get_nonexistent_acl(self) -> None:
        """Test retrieving ACL for a non-existent resource."""
        non_existent_id = uuid4()
        assert ACLRegistry.get_acl(non_existent_id) == []


class TestAccessControl:
    """
    Test suite for AccessControl class functionality.
    Tests permission checking and access control enforcement.
    """

    @pytest.fixture
    def mock_user_principals_getter(self) -> list[Principal]:
        """Fixture providing mock user principals."""
        return [UserPrincipal("user1"), RolePrincipal("editor")]

    @pytest.fixture
    def access_control(self, mock_user_principals_getter) -> AccessControl:
        """Fixture providing AccessControl instance."""
        return AccessControl(
            user_principals_getter=lambda: mock_user_principals_getter,
            permission_exception=HTTPException(status_code=403, detail="Forbidden"),
        )

    def test_has_permission_single_resource(self, access_control) -> None:
        """Test permission checking for a single resource."""
        resource = MockResource()
        principals = [UserPrincipal("user1")]

        assert access_control.has_permission(principals=principals, required_permissions="edit", resource=resource)

    def test_has_permission_multiple_resources(self, access_control) -> None:
        """Test permission checking across multiple resources."""
        resource1 = MockResource()
        resource2 = MockResource()
        principals = [UserPrincipal("user1")]

        assert access_control.has_permission(
            principals=principals, required_permissions="edit", resource=[resource1, resource2]
        )

    def test_show_permissions(self, access_control) -> None:
        """Test retrieval of all permissions for a user."""
        resource = MockResource()
        principals = [UserPrincipal("user1")]

        permissions = access_control.show_permissions(principals, resource)
        assert set(permissions) == {"view", "edit", "delete"}

    def test_assert_access_raises_exception(self, access_control) -> None:
        """Test that assert_access raises exception for unauthorized access."""
        resource = MockResource()
        principals = [UserPrincipal("unauthorized_user")]

        with pytest.raises(HTTPException) as exc_info:
            access_control.assert_access(principals, "edit", resource)
        assert exc_info.value.status_code == 403


class TestAllowAll:
    """
    Test suite for AllowAll class functionality.
    Tests the wildcard permission matching behavior.
    """

    def test_allow_all_contains(self) -> None:
        """Test that AllowAll matches any permission."""
        allow_all = AllowAll()
        assert "any_permission" in allow_all
        assert "another_permission" in allow_all

    def test_allow_all_string_representation(self) -> None:
        """Test string representation of AllowAll."""
        allow_all = AllowAll()
        assert str(allow_all) == "*"
        assert repr(allow_all) == "*"
