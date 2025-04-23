from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Mixin to add timestamp fields for created, updated, and deleted times to a model.

    This mixin adds `created`, `updated`, and `deleted` fields to a model, where:
    - `created` is the timestamp of creation (set to current time on object creation).
    - `updated` is the timestamp of the last update (set to current time on each update).
    - `deleted` is the timestamp of deletion (nullable).
    """

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=None,
        nullable=True,
    )
