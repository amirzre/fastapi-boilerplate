from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    limit: int = Field(..., description="The number of items per page.")
    offset: int = Field(..., description="The starting position of the items.")
    total: int = Field(..., description="Total number of items available.")
    items: Sequence[T] = Field(..., description="The list of items for the current page.")

    model_config = ConfigDict(from_attributes=True)
