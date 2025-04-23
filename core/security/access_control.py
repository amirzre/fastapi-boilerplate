import functools
from dataclasses import dataclass
from typing import Any, List, Set, Tuple, TypeVar, Union, cast

from fastapi import Depends, HTTPException, status
from pydantic import UUID4

DefaultException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


Allow: str = "allow"
Deny: str = "deny"

# Type alias for ACL entries
ACLEntry = Tuple[str, "Principal", List[str]]
ACLList = List[ACLEntry]

T = TypeVar("T")


@dataclass(frozen=True)
class Principal:
    """
    Represents a principal (user, role, system, etc.) used in ACLs.
    """

    key: str
    value: str

    def __repr__(self) -> str:
        return f"{self.key}:{self.value}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class SystemPrincipal(Principal):
    """
    Represents a system-wide principal such as 'everyone' or 'authenticated'.
    """

    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="system", value=value, *args, **kwargs)


@dataclass(frozen=True)
class UserPrincipal(Principal):
    """
    Represents a user-specific principal.
    """

    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="user", value=value, *args, **kwargs)


@dataclass(frozen=True)
class RolePrincipal(Principal):
    """
    Represents a role-specific principal.
    """

    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="role", value=value, *args, **kwargs)


@dataclass(frozen=True)
class PostPrincipal(Principal):
    """
    Represents a post-specific principal (custom use case).
    """

    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="post", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ActionPrincipal(Principal):
    """
    Represents an action-specific principal (custom use case).
    """

    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="action", value=value, *args, **kwargs)


class ACLRegistry:
    """
    Registry to hold ACLs for resources using their UUID or integer IDs.
    """

    _acl_map: dict[Union[UUID4, int], ACLList] = {}

    @classmethod
    def set_acl(cls, resource_id: Union[UUID4, int], acl: ACLList) -> None:
        """Set ACL for a specific resource."""
        cls._acl_map[resource_id] = acl

    @classmethod
    def get_acl(cls, resource_id: Union[UUID4, int]) -> ACLList:
        """Retrieve ACL for a specific resource."""
        return cls._acl_map.get(resource_id, [])


Everyone = SystemPrincipal(value="everyone")
Authenticated = SystemPrincipal(value="authenticated")


class AllowAll:
    """
    A container that allows all access. Used in permissive configurations.
    """

    def __contains__(self, item: Any) -> bool:
        return True

    def __repr__(self) -> str:
        return "*"

    def __str__(self) -> str:
        return self.__repr__()


class AccessControl:
    """
    Class for enforcing permission checks based on defined ACLs.
    """

    def __init__(
        self,
        user_principals_getter: Any,
        permission_exception: Any = DefaultException,
    ) -> None:
        """
        Initialize AccessControl.

        Args:
            user_principals_getter: A dependency that returns a list of principals for the current user.
            permission_exception: The exception to raise on access denial.
        """
        self.user_principals_getter = user_principals_getter
        self.permission_exception = permission_exception

    def __call__(self, permissions: Union[str, List[str]]):
        """
        Return a FastAPI dependency to enforce permission checks.
        """

        def _permission_dependency(principals=Depends(self.user_principals_getter)):
            assert_access = functools.partial(self.assert_access, principals, permissions)
            return assert_access

        return _permission_dependency

    def assert_access(self, principals: List[Principal], permissions: Union[str, List[str]], resource: Any) -> None:
        """
        Assert that the user has permission to access the resource.

        Raises:
            HTTPException: If access is not permitted.
        """
        if not self.has_permission(
            principals=principals,
            required_permissions=permissions,
            resource=resource,
        ):
            raise self.permission_exception

    def has_permission(
        self, principals: List[Principal], required_permissions: Union[str, List[str]], resource: Any
    ) -> bool:
        """
        Check if the given principals have the required permissions for the resource.
        """
        if not isinstance(resource, list):
            resource = [resource]

        permits = []
        for resource_obj in resource:
            granted = False
            acl = self._acl(resource_obj)

            # Convert required_permissions to list if it's a string
            permissions_list: List[str] = (
                [required_permissions] if isinstance(required_permissions, str) else required_permissions
            )

            for action, principal, permission in acl:
                is_required_permissions_in_permission = any(
                    required_permission in permission for required_permission in permissions_list
                )

                if (action == Allow and is_required_permissions_in_permission) and (
                    principal in principals or principal == Everyone
                ):
                    granted = True
                    break
            permits.append(granted)

        return all(permits)

    def show_permissions(self, principals: List[Principal], resource: Any) -> List[str]:
        """
        Show a list of permissions granted to the given principals for the resource.
        """
        if not isinstance(resource, list):
            resource = [resource]

        all_permissions: List[List[List[str]]] = []

        for resource_obj in resource:
            resource_permissions: List[List[str]] = []
            acl = self._acl(resource_obj)

            for action, principal, permission in acl:
                if (action == Allow and principal in principals) or principal == Everyone:
                    # Append the permission list to our resource_permissions
                    resource_permissions.append(permission)

            all_permissions.append(resource_permissions)

        # Flatten first to handle nested lists properly
        flattened_permissions = [self._flatten(resource_perms) for resource_perms in all_permissions]

        # If we have permissions to intersect
        if flattened_permissions and all(flattened_permissions):
            result_set: Set[str] = functools.reduce(set.intersection, map(set, flattened_permissions))
            return list(result_set)
        return []

    def _acl(self, resource: Any) -> ACLList:
        """
        Extract ACL from the resource, checking for __acl__ or using the ACLRegistry.
        """
        if hasattr(resource, "__acl__"):
            acl = resource.__acl__
            if callable(acl):
                return cast(ACLList, acl())
            return cast(ACLList, acl)

        resource_id = getattr(resource, "uuid", None)
        if resource_id:
            return ACLRegistry.get_acl(resource_id)

        return []

    def _flatten(self, any_list: List[Any]) -> List[Any]:
        """
        Recursively flatten a nested list.
        """
        flat_list: List[Any] = []
        for element in any_list:
            if isinstance(element, list):
                flat_list += self._flatten(element)
            else:
                flat_list.append(element)
        return flat_list
