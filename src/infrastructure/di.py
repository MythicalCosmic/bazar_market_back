from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.repositories.user_repo import UserRepository, AddressRepository
from src.core.services.user_service import UserService
from src.core.services.auth_service import AuthService
from src.infrastructure.redis import get_redis, RedisCache


async def get_cache(redis: Redis = Depends(get_redis)) -> RedisCache:
    return RedisCache(redis)


async def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


async def get_address_repo(session: AsyncSession = Depends(get_session)) -> AddressRepository:
    return AddressRepository(session)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    address_repo: AddressRepository = Depends(get_address_repo),
) -> UserService:
    return UserService(user_repo, address_repo)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    cache: RedisCache = Depends(get_cache),
) -> AuthService:
    return AuthService(user_repo, cache)
