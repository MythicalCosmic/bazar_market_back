from fastapi import Depends, Header

from src.core.enums import UserRole, AdminPermission
from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.dto.user import UserDTO
from src.core.services.auth_service import AuthService
from src.core.services.user_service import UserService
from src.infrastructure.di import get_user_service, get_auth_service, get_cache
from src.infrastructure.redis import RedisCache


def require_permission(*required: AdminPermission):
    """Factory that returns a dependency checking admin session + permissions."""

    async def dependency(
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

        user_perms = session.get("permissions", [])
        for perm in required:
            if perm.value not in user_perms:
                raise ForbiddenException(f"Missing permission: {perm.value}")

        return user

    return dependency


async def get_current_customer(
    x_telegram_id: int = Header(...),
    user_service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
) -> int:
    """Returns the user's DB id from their telegram_id.
    Later this will be replaced with SMS token auth."""

    cached = await cache.get(f"customer:tg:{x_telegram_id}")
    if cached:
        return cached["user_id"]

    try:
        user = await user_service.get_user_by_telegram_id(x_telegram_id)
    except NotFoundException:
        raise ForbiddenException("User not found for this telegram_id")

    await cache.set(f"customer:tg:{x_telegram_id}", {"user_id": user.id}, ttl=600)
    return user.id
