from enum import auto

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from core.db.mixins import IDUUIDMixin, TimestampMixin
from core.enum import StrEnum


class UserRole(StrEnum):
    ADMIN = auto()
    USER = auto()


class User(Base, IDUUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    activated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
