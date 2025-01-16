from enum import auto

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.db.mixins import IDUUIDMixin, TimestampMixin
from core.enum import StrEnum


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
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="posts", cascade="all, delete-orphan")
