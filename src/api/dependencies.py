from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis

from src.core.enums import UserRole
from src.core.exceptions import ForbiddenException
from src.core.dto.user import UserDTO
from src.core.services.auth_service import AuthService
from src.core.services.user_service import UserService
from src.infrastructure.di import get_user_service, get_auth_service
from src.infrastructure.redis import get_redis, RedisCache

bearer_scheme = HTTPBearer()


async def get_cache(redis: Redis = Depends(get_redis)) -> RedisCache:
    return RedisCache(redis)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> UserDTO:
    payload = auth_service.decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise ForbiddenException("Invalid access token")

    user_id = int(payload["sub"])
    user = await user_service.get_user(user_id)

    if not user.is_active:
        raise ForbiddenException("Account is deactivated")
    if user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required")

    await user_service.touch_last_seen(user_id)
    return user
