import pickle
from typing import Any
from uuid import UUID

import orjson
from pydantic import BaseModel

from core.cache.base import BaseBackend
from core.redis import redis_client as redis


class RedisBackend(BaseBackend):
    async def get(self, key: str, model: BaseModel = None) -> Any:
        result = await redis.get(key)
        if not result:
            return

        try:
            data = orjson.loads(result.encode("utf8"))
            return model(**data) if model else data
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        if isinstance(response, BaseModel):
            data = response.model_dump()

            def convert_uuids(obj):
                if isinstance(obj, UUID):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: convert_uuids(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_uuids(i) for i in obj]
                return obj

            data = convert_uuids(data)
            response = orjson.dumps(data)
        elif isinstance(response, dict):
            response = pickle.dumps(response)
        else:
            response = pickle.dumps(response)

        await redis.set(name=key, value=response, ex=ttl)

    async def delete_startswith(self, value: str) -> None:
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)
