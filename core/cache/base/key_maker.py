from abc import ABC, abstractmethod
from typing import Callable


class BaseKeyMaker(ABC):
    """
    Abstract base class for generating cache keys.

    This class defines the interface for creating unique cache keys based on a function and prefix.
    """

    @abstractmethod
    async def make(self, function: Callable, prefix: str) -> str:
        """
        Generate a cache key based on the function and a prefix.

        Args:
            function (Callable): The function for which to generate the cache key.
            prefix (str): The prefix to add to the cache key.

        Returns:
            str: The generated cache key.
        """
        ...
