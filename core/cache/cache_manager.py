from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from core.cache.base import BaseBackend, BaseKeyMaker
from core.cache.cache_tag import CacheTag

F = TypeVar("F", bound=Callable[..., Any])


class CacheManager:
    """
    Manages caching operations including setting, retrieving, and invalidating cache
    for functions using decorators. Supports caching with tags or prefixes and
    integrates with the specified backend and key maker.
    """
    def __init__(self):
        """
        Initializes the CacheManager with optional backend and key maker.
        """
        self.backend: Optional[BaseBackend] = None
        self.key_maker: Optional[BaseKeyMaker] = None

    def init(self, *, backend: BaseBackend, key_maker: BaseKeyMaker) -> None:
        """
        Initializes the cache manager with the specified backend and key maker.

        Args:
            backend (BaseBackend): The caching backend to use.
            key_maker (BaseKeyMaker): The key maker used for generating cache keys.
        """
        self.backend = backend
        self.key_maker = key_maker

    def cached(
        self,
        *,
        prefix: Optional[str] = None,
        tag: Optional[CacheTag] = None,
        ttl: int = 60,
    ) -> Callable[[F], F]:
        """
        Decorator to cache the result of a function call.

        This decorator stores the result of the function in the cache if it's not
        already cached, and retrieves it from the cache if it exists.

        Args:
            prefix (Optional[str]): The prefix for the cache key.
            tag (Optional[CacheTag]): A cache tag to use in the key generation.
            ttl (int): Time-to-live (TTL) for the cache, in seconds. Default is 60.

        Returns:
            Callable[[F], F]: The decorated function.
        """

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
        """
        Decorator to invalidate cache entries by prefix.

        This decorator deletes all cache entries that start with the given prefix.

        Args:
            prefix (str): The prefix to use for invalidating cache entries.

        Returns:
            Callable[[F], F]: The decorated function.
        """

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
        """
        Decorator to invalidate cache entries by tag.

        This decorator deletes all cache entries associated with the given tag.

        Args:
            tag (CacheTag): The tag to use for invalidating cache entries.

        Returns:
            Callable[[F], F]: The decorated function.
        """

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
        """
        Remove all cache entries associated with a specific tag.

        Args:
            tag (CacheTag): The tag whose associated cache entries should be removed.
        """
        if not self.backend:
            raise Exception("backend is None.")
        await self.backend.delete_startswith(value=tag.value)

    async def remove_by_prefix(self, *, prefix: str) -> None:
        """
        Remove all cache entries that start with the given prefix.

        Args:
            prefix (str): The prefix whose associated cache entries should be removed.
        """
        if not self.backend:
            raise Exception("backend is None.")
        await self.backend.delete_startswith(value=prefix)


Cache = CacheManager()
