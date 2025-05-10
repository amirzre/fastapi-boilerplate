import inspect
from typing import Callable

from core.cache.base import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
    """
    Custom key maker for generating cache keys based on function name, module, and parameters.
    """

    async def make(self, function: Callable, prefix: str) -> str:
        """
        Generates a unique cache key based on the function, its module, and parameters.

        Args:
            function (Callable): The function whose result is being cached.
            prefix (str): The prefix to prepend to the generated cache key.

        Returns:
            str: The generated cache key.
        """
        module = inspect.getmodule(function)
        module_name = module.__name__ if module is not None else "unknown"

        path = f"{prefix}::{module_name}::{function.__name__}"

        args = "".join(param.name for param in inspect.signature(function).parameters.values())

        return f"{path}.{args}" if args else path
