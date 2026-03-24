import os
import json
from redis.asyncio import Redis, ConnectionPool

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_DB = os.environ.get("REDIS_DATABASE", "0")

pool = ConnectionPool.from_url(REDIS_URL)


async def get_redis() -> Redis:
    return Redis(connection_pool=pool, db=REDIS_DB)


class RedisCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> dict | list | None:
        data = await self.redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(self, key: str, value: dict | list, ttl: int = 300) -> None:
        await self.redis.set(key, json.dumps(value, default=str), ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
