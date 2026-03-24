from fastapi import Depends, Header

from src.core.enums import UserRole
from src.core.exceptions import ForbiddenException
from src.core.dto.user import UserDTO
from src.core.services.auth_service import AuthService
from src.core.services.user_service import UserService
from src.infrastructure.di import get_user_service, get_auth_service, get_cache
from src.infrastructure.redis import RedisCache


async def get_current_admin(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
) -> UserDTO:
    if not authorization.startswith("Bearer "):
        raise ForbiddenException("Invalid authorization header")

    token = authorization[7:]
    session = await auth_service.validate_session(token)
    user_id = session["user_id"]

    cached_user = await cache.get(f"admin:session:{user_id}")
    if cached_user:
        user = UserDTO.model_validate(cached_user)
    else:
        user = await user_service.get_user(user_id)
        await cache.set(f"admin:session:{user_id}", user.model_dump(), ttl=300)

    if not user.is_active:
        raise ForbiddenException("Account is deactivated")
    if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise ForbiddenException("Admin access required")

    await user_service.touch_last_seen(user_id)
    return user
