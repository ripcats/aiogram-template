from typing import Any

import orjson
from redis.asyncio import Redis

from app.application.interfaces.cache import ICacheService
from app.config import RedisConfig


def build_redis(config: RedisConfig) -> Redis:  # type: ignore[type-arg]
    return Redis.from_url(
        config.dsn,
        encoding="utf-8",
        decode_responses=False,
    )


class RedisCacheService(ICacheService):
    def __init__(self, redis: Redis) -> None:  # type: ignore[type-arg]
        self._redis = redis

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        return orjson.loads(raw) if raw is not None else None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        encoded = orjson.dumps(value)
        if ttl_seconds is not None:
            await self._redis.setex(key, ttl_seconds, encoded)
        else:
            await self._redis.set(key, encoded)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(key))

    async def increment(self, key: str, amount: int = 1) -> int:
        return int(await self._redis.incrby(key, amount))

    async def expire(self, key: str, ttl_seconds: int) -> None:
        await self._redis.expire(key, ttl_seconds)

    async def ttl(self, key: str) -> int | None:
        ttl = int(await self._redis.ttl(key))
        return ttl if ttl >= 0 else None
