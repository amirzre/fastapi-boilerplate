from enum import auto

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.db.mixins import IDUUIDMixin, TimestampMixin
from core.enum import StrEnum
from core.security import Allow, Everyone, RolePrincipal, UserPrincipal


class UserPermission(StrEnum):
    READ = auto()
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


class UserRole(StrEnum):
    ADMIN = auto()
    USER = auto()


class User(Base, IDUUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.USER, nullable=False)
    activated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")

    def __acl__(self):
        basic_permissions = [UserPermission.CREATE]
        self_permissions = [UserPermission.READ, UserPermission.UPDATE, UserPermission.DELETE]
        all_permissions = list(UserPermission)

        return [
            (Allow, Everyone, basic_permissions),
            (Allow, UserPrincipal(str(self.uuid)), self_permissions),
            (Allow, RolePrincipal(UserRole.ADMIN), all_permissions),
        ]
