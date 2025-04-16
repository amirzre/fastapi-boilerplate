from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from core.cache.base import BaseBackend, BaseKeyMaker
from core.cache.cache_tag import CacheTag

F = TypeVar("F", bound=Callable[..., Any])


class CacheManager:
    def __init__(self):
        self.backend: Optional[BaseBackend] = None
        self.key_maker: Optional[BaseKeyMaker] = None

    def init(self, *, backend: BaseBackend, key_maker: BaseKeyMaker) -> None:
        self.backend = backend
        self.key_maker = key_maker

    def cached(
        self,
        *,
        prefix: Optional[str] = None,
        tag: Optional[CacheTag] = None,
        ttl: int = 60,
    ) -> Callable[[F], F]:
        """Decorator to cache data."""

        def _cached(function: F) -> F:
            @wraps(function)
            async def __cached(*args: Any, **kwargs: Any) -> Any:
                if not self.backend or not self.key_maker:
                    raise Exception("backend or key_maker is None")

                key = await self.key_maker.make(
                    function=function,
                    prefix=prefix if prefix else tag.value if tag else "",
                )

                cached_response = await self.backend.get(key=key)
                if cached_response:
                    return cached_response

                response = await function(*args, **kwargs)
                await self.backend.set(response=response, key=key, ttl=ttl)
                return response

            return cast(F, __cached)

        return _cached

    def invalidate_by_prefix(self, prefix: str) -> Callable[[F], F]:
        """Decorator to invalidate cache by prefix."""

        def _invalidate(function: F) -> F:
            @wraps(function)
            async def __invalidate(*args: Any, **kwargs: Any) -> Any:
                if not self.backend:
                    raise Exception("backend is None.")

                await self.backend.delete_startswith(value=prefix)
                return await function(*args, **kwargs)

            return cast(F, __invalidate)

        return _invalidate

    def invalidate_by_tag(self, tag: CacheTag) -> Callable[[F], F]:
        """Decorator to invalidate cache by tag."""

        def _invalidate(function: F) -> F:
            @wraps(function)
            async def __invalidate(*args: Any, **kwargs: Any) -> Any:
                if not self.backend:
                    raise Exception("backend is None.")

                await self.backend.delete_startswith(value=tag.value)
                return await function(*args, **kwargs)

            return cast(F, __invalidate)

        return _invalidate

    async def remove_by_tag(self, *, tag: CacheTag) -> None:
        if not self.backend:
            raise Exception("backend is None.")
        await self.backend.delete_startswith(value=tag.value)

    async def remove_by_prefix(self, *, prefix: str) -> None:
        if not self.backend:
            raise Exception("backend is None.")
        await self.backend.delete_startswith(value=prefix)


Cache = CacheManager()
