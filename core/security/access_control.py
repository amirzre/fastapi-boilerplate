import functools
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from pydantic import UUID4

DefaultException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


Allow: str = "allow"
Deny: str = "deny"


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
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="system", value=value, *args, **kwargs)


@dataclass(frozen=True)
class UserPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="user", value=value, *args, **kwargs)


@dataclass(frozen=True)
class RolePrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="role", value=value, *args, **kwargs)


@dataclass(frozen=True)
class PostPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="post", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ActionPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="action", value=value, *args, **kwargs)


class ACLRegistry:
    _acl_map: dict[UUID4 | int, list[tuple[str, Principal, list[str]]]] = {}

    @classmethod
    def set_acl(cls, resource_id: UUID4 | int, acl: list[tuple[str, Principal, list[str]]]):
        cls._acl_map[resource_id] = acl

    @classmethod
    def get_acl(cls, resource_id: UUID4 | int):
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

    def __call__(self, permissions: str):
        def _permission_dependency(principals=Depends(self.user_principals_getter)):
            assert_access = functools.partial(self.assert_access, principals, permissions)
            return assert_access

        return _permission_dependency

    def assert_access(self, principals: list, permissions: str, resource: Any):
        if not self.has_permission(
            principals=principals,
            required_permissions=permissions,
            resource=resource,
        ):
            raise self.permission_exception

    def has_permission(self, principals: list[Principal], required_permissions: str, resource: Any):
        if not isinstance(resource, list):
            resource = [resource]

        permits = []
        for resource_obj in resource:
            granted = False
            acl = self._acl(resource_obj)
            if not isinstance(required_permissions, list):
                required_permissions = [required_permissions]

            for action, principal, permission in acl:
                is_required_permissions_in_permission = any(
                    required_permission in permission for required_permission in required_permissions
                )

                if (action == Allow and is_required_permissions_in_permission) and (
                    principal in principals or principal == Everyone
                ):
                    granted = True
                    break
            permits.append(granted)

        return all(permits)

    def show_permissions(self, principals: list[Principal], resource: Any):
        if not isinstance(resource, list):
            resource = [resource]

        permissions = []
        for resource_obj in resource:
            local_permissions = []
            acl = self._acl(resource_obj)

            for action, principal, permission in acl:
                if action == Allow and principal in principals or principal == Everyone:
                    local_permissions.append(permission)

            permissions.append(local_permissions)

        # get intersection of permissions
        permissions = [self._flatten(permission) for permission in permissions]
        permissions = functools.reduce(set.intersection, map(set, permissions))

        return list(permissions)

    def _acl(self, resource):
        if hasattr(resource, "__acl__"):
            acl = resource.__acl__
            if callable(acl):
                return acl()
            return acl

        resource_id = getattr(resource, "uuid", None)
        if resource_id:
            return ACLRegistry.get_acl(resource_id)

        return []

    def _flatten(self, any_list: list[Any]) -> list[Any]:
        flat_list = []
        for element in any_list:
            if isinstance(element, list):
                flat_list += self._flatten(element)
            else:
                flat_list.append(element)
        return flat_list
