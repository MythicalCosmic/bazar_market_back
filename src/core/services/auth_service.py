import secrets

import bcrypt

from src.core.dto.auth import AdminLoginDTO, SessionDTO
from src.core.enums import UserRole
from src.core.exceptions import ForbiddenException
from src.core.interfaces.user_interface import IUserRepository
from src.infrastructure.config import settings
from src.infrastructure.redis import RedisCache


class AuthService:
    SESSION_PREFIX = "session:"

    def __init__(self, user_repo: IUserRepository, cache: RedisCache):
        self.user_repo = user_repo
        self.cache = cache

    async def admin_login(self, dto: AdminLoginDTO) -> SessionDTO:
        user = await self.user_repo.get_by_username(dto.username)
        if not user:
            raise ForbiddenException("Invalid credentials")
        if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
            raise ForbiddenException("Admin access required")
        if not user.password_hash:
            raise ForbiddenException("No password set for this account")
        if not self.verify_password(dto.password, user.password_hash):
            raise ForbiddenException("Invalid credentials")
        if not user.is_active:
            raise ForbiddenException("Account is deactivated")

        session_token = secrets.token_urlsafe(48)
        permissions = user.permissions or []
        session_data = {
            "data": {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "permissions": permissions,
            }
        }
        await self.cache.set(
            f"{self.SESSION_PREFIX}{session_token}",
            session_data,
            ttl=settings.SESSION_TTL,
        )

        return SessionDTO(
            session_token=session_token,
            user_id=user.id,
            role=user.role,
            permissions=permissions,
            expires_in=settings.SESSION_TTL,
        )

    async def validate_session(self, session_token: str) -> dict:
        data = await self.cache.get(f"{self.SESSION_PREFIX}{session_token}")
        if not data:
            raise ForbiddenException("Session expired or invalid")
        return data

    async def logout(self, session_token: str) -> None:
        await self.cache.delete(f"{self.SESSION_PREFIX}{session_token}")

    async def logout_all(self, user_id: int) -> None:
        await self.cache.delete_pattern(f"{self.SESSION_PREFIX}*")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
