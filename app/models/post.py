from enum import auto

from pydantic import UUID4
from sqlalchemy import UUID, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import UserRole
from core.db import Base
from core.db.mixins import IDUUIDMixin, TimestampMixin
from core.enum import StrEnum
from core.security import Allow, Authenticated, RolePrincipal, UserPrincipal


class PostPermission(StrEnum):
    READ = auto()
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


class PostStatus(StrEnum):
    DRAFT = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()


class Post(Base, IDUUIDMixin, TimestampMixin):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status"), default=PostStatus.DRAFT, nullable=False
    )
    user_id: Mapped[UUID4] = mapped_column(UUID, ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="posts")

    def __acl__(self):
        basic_permission = [PostPermission.CREATE]
        self_permission = [PostPermission.READ, PostPermission.UPDATE, PostPermission.DELETE]
        all_permission = list(PostPermission)

        return [
            (Allow, Authenticated, basic_permission),
            (Allow, UserPrincipal(str(self.user_id)), self_permission),
            (Allow, RolePrincipal(UserRole.ADMIN), all_permission),
        ]
