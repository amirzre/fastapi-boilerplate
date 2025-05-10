import pickle
from typing import Any, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel

from core.cache.base import BaseBackend
from core.redis import redis_client as redis


class RedisBackend(BaseBackend):
    """
    Redis-backed cache storage for retrieving, storing, and deleting cache entries.
    """

    async def get(self, key: str, model: Optional[type[BaseModel]] = None) -> Any:
        """
        Retrieves data from Redis and optionally parses it into a Pydantic model.

        Args:
            key (str): The cache key to look up.
            model (Optional[type[BaseModel]]): The Pydantic model to parse the cached data into.

        Returns:
            Any: The cached data, parsed into the model if provided, otherwise raw data.
        """
        result = await redis.get(key)
        if not result:
            return

        try:
            data = orjson.loads(result.encode("utf8"))
            return model(**data) if model else data
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        """
        Stores data in Redis, serializing the response before storing it.

        Args:
            response (Any): The response data to store in the cache.
            key (str): The cache key under which the data will be stored.
            ttl (int): The time-to-live (TTL) for the cache entry in seconds. Default is 60.
        """
        serialized_data = self._serialize_response(response=response)
        await redis.set(name=key, value=serialized_data, ex=ttl)

    async def delete_startswith(self, value: str) -> None:
        """
        Deletes all keys in Redis that start with the given prefix.

        Args:
            value (str): The prefix used to match and delete cache entries.
        """
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)

    @staticmethod
    def _serialize_response(response: BaseModel | dict | Any) -> bytes:
        """
        Serializes the response for Redis storage, handling various response types.

        Args:
            response (BaseModel | dict | Any): The response data to serialize.

        Returns:
            bytes: The serialized response data.
        """
        if isinstance(response, BaseModel):
            data = response.model_dump()
            data = RedisBackend._convert_uuids(data)
            return orjson.dumps(data)
        elif isinstance(response, dict):
            return pickle.dumps(response)
        return pickle.dumps(response)

    @staticmethod
    def _convert_uuids(data: Any) -> Any:
        """
        Recursively converts UUIDs to strings in a dictionary or list.

        Args:
            data (Any): The data structure (dictionary or list) to convert UUIDs in.

        Returns:
            Any: The data structure with UUIDs converted to strings.
        """
        if isinstance(data, UUID):
            return str(data)
        elif isinstance(data, dict):
            return {k: RedisBackend._convert_uuids(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [RedisBackend._convert_uuids(item) for item in data]
        return data
