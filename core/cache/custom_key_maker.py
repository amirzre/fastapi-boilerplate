import inspect
from typing import Callable

from core.cache.base import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
    async def make(self, function: Callable, prefix: str) -> str:
        module = inspect.getmodule(function)
        module_name = module.__name__ if module is not None else "unknown"

        path = f"{prefix}::{module_name}::{function.__name__}"

        args = "".join(param.name for param in inspect.signature(function).parameters.values())

        return f"{path}.{args}" if args else path
