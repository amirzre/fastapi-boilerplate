from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import UUID, BigInteger
from sqlalchemy.orm import Mapped, mapped_column


class IDMixin:
    """
    Mixin to add an auto-incrementing `id` field to a model.

    This mixin adds a primary key `id` field to a model, with `BigInteger` as
    its type and auto-increment functionality.
    """

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class UUIDMixin:
    """
    Mixin to add a `uuid` field to a model.

    This mixin adds a unique `uuid` field to a model, which serves as a
    universally unique identifier for instances of the model. It is set as
    the primary key and has an index for fast lookup.
    """

    uuid: Mapped[UUID4] = mapped_column(primary_key=True, unique=True, index=True, default=uuid4)


class IDUUIDMixin:
    """
    Mixin to add both an auto-incrementing `id` field and a `uuid` field to a model.

    This mixin combines the functionality of `IDMixin` and `UUIDMixin`, adding both
    an auto-incrementing primary key `id` and a unique `uuid` field.
    """

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID4] = mapped_column(UUID, unique=True, index=True, default=uuid4)
