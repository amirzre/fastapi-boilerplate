from abc import ABC, abstractmethod
from typing import Any


class BaseBackend(ABC):
    """
    Abstract base class for defining cache backend operations.

    This class defines the interface for interacting with a cache backend,
    including methods for retrieving, storing, and deleting cache entries.
    """

    @abstractmethod
    async def get(self, key: str) -> Any:
        """
        Retrieve a cached value by its key.

        Args:
            key (str): The key associated with the cached data.

        Returns:
            Any: The cached data, or `None` if the key doesn't exist in the cache.
        """
        ...

    @abstractmethod
    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        """
        Store data in the cache under a specified key.

        Args:
            response (Any): The data to store in the cache.
            key (str): The key to associate with the stored data.
            ttl (int, optional): The time-to-live (TTL) for the cached data in seconds. Default is 60.

        Returns:
            None
        """
        ...

    @abstractmethod
    async def delete_startswith(self, value: str) -> None:
        """
        Delete all cache entries whose keys start with the specified value.

        Args:
            value (str): The prefix of the keys to delete.

        Returns:
            None
        """
        ...
