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
    key: str
    value: str

    def __repr__(self) -> str:
        return f"{self.key}:{self.value}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class SystemPrincipal(Principal):
    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="system", value=value, *args, **kwargs)


@dataclass(frozen=True)
class UserPrincipal(Principal):
    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="user", value=value, *args, **kwargs)


@dataclass(frozen=True)
class RolePrincipal(Principal):
    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="role", value=value, *args, **kwargs)


@dataclass(frozen=True)
class PostPrincipal(Principal):
    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="post", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ActionPrincipal(Principal):
    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(key="action", value=value, *args, **kwargs)


class ACLRegistry:
    _acl_map: dict[Union[UUID4, int], ACLList] = {}

    @classmethod
    def set_acl(cls, resource_id: Union[UUID4, int], acl: ACLList) -> None:
        cls._acl_map[resource_id] = acl

    @classmethod
    def get_acl(cls, resource_id: Union[UUID4, int]) -> ACLList:
        return cls._acl_map.get(resource_id, [])


Everyone = SystemPrincipal(value="everyone")
Authenticated = SystemPrincipal(value="authenticated")


class AllowAll:
    def __contains__(self, item: Any) -> bool:
        return True

    def __repr__(self) -> str:
        return "*"

    def __str__(self) -> str:
        return self.__repr__()


class AccessControl:
    def __init__(
        self,
        user_principals_getter: Any,
        permission_exception: Any = DefaultException,
    ) -> None:
        self.user_principals_getter = user_principals_getter
        self.permission_exception = permission_exception

    def __call__(self, permissions: Union[str, List[str]]):
        def _permission_dependency(principals=Depends(self.user_principals_getter)):
            assert_access = functools.partial(self.assert_access, principals, permissions)
            return assert_access

        return _permission_dependency

    def assert_access(self, principals: List[Principal], permissions: Union[str, List[str]], resource: Any) -> None:
        if not self.has_permission(
            principals=principals,
            required_permissions=permissions,
            resource=resource,
        ):
            raise self.permission_exception

    def has_permission(
        self, principals: List[Principal], required_permissions: Union[str, List[str]], resource: Any
    ) -> bool:
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
        flat_list: List[Any] = []
        for element in any_list:
            if isinstance(element, list):
                flat_list += self._flatten(element)
            else:
                flat_list.append(element)
        return flat_list
