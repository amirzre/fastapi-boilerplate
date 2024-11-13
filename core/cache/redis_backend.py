import pickle
from typing import Any, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel

from core.cache.base import BaseBackend
from core.redis import redis_client as redis


class RedisBackend(BaseBackend):
    async def get(self, key: str, model: Optional[type[BaseModel]] = None) -> Any:
        """Retrieve data from Redis and optionally parse it into a Pydantic model."""
        result = await redis.get(key)
        if not result:
            return

        try:
            data = orjson.loads(result.encode("utf8"))
            return model(**data) if model else data
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        """Store data in Redis, serializing based on response type and setting expiration."""
        serialized_data = self._serialize_response(response=response)
        await redis.set(name=key, value=serialized_data, ex=ttl)

    async def delete_startswith(self, value: str) -> None:
        """Delete all keys in Redis that start with a given prefix."""
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)

    @staticmethod
    def _serialize_response(response: BaseModel | dict | Any) -> bytes:
        """Serialize a response based on its type for Redis storage."""
        if isinstance(response, BaseModel):
            data = response.model_dump()
            data = RedisBackend._convert_uuids(data)
            return orjson.dumps(data)
        elif isinstance(response, dict):
            return pickle.dumps(response)
        return pickle.dumps(response)

    @staticmethod
    def _convert_uuids(data: Any) -> Any:
        """Recursively convert UUIDs to strings in a dictionary or list."""
        if isinstance(data, UUID):
            return str(data)
        elif isinstance(data, dict):
            return {k: RedisBackend._convert_uuids(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [RedisBackend._convert_uuids(item) for item in data]
        return data
