from redis.asyncio import Redis, ConnectionPool
from src.infrastructure.config import settings


pool = ConnectionPool.from_url(settings.redis_url)


async def get_redis() -> Redis:
    return Redis(connection_pool=pool, db=settings.redis_database)

