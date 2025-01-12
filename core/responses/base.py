from enum import auto
from http import HTTPStatus
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from core.enum import StrEnum
from core.i18n import translate as _

T = TypeVar("T")


class ResponseStatus(StrEnum):
    SUCCESS = auto()
    FAILURE = auto()


class APIResponseHeader(BaseModel):
    """Header type for API responses."""

    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default=_("Operation completed successfully."))
    code: int = Field(default=HTTPStatus.OK)


class APIResponseType(BaseModel, Generic[T]):
    """Type definition for API responses."""

    header: APIResponseHeader
    content: Optional[T] = None


class APIResponse(APIResponseType[T], Generic[T]):
    """
    Generic API response wrapper with automatic exception handling.
    """

    def __init__(self, data: T):
        super().__init__(
            header=APIResponseHeader(
                status=ResponseStatus.SUCCESS,
                message=_("Operation completed successfully."),
                code=HTTPStatus.OK,
            ),
            content=data,
        )
