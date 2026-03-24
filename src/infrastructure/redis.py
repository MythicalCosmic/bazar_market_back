import json
from redis.asyncio import Redis, ConnectionPool
from src.infrastructure.config import settings

pool = ConnectionPool.from_url(settings.redis_url)


async def get_redis() -> Redis:
    return Redis(connection_pool=pool, db=settings.redis_database)


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
