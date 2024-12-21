from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import UUID, BigInteger
from sqlalchemy.orm import Mapped, mapped_column


class IDMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class UUIDMixin:
    uuid: Mapped[UUID4] = mapped_column(primary_key=True, unique=True, index=True, default=uuid4)


class IDUUIDMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID4] = mapped_column(UUID, unique=True, index=True, default=uuid4)
