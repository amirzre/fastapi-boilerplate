from enum import StrEnum, auto


class CacheTag(StrEnum):
    """
    Enum representing various cache tags for grouping cache entries.
    """
    GET_USER_LIST = auto()
