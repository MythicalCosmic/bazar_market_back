from datetime import datetime, timezone, timedelta

import bcrypt
import jwt

from src.core.dto.auth import AdminLoginDTO, TokenDTO
from src.core.enums import UserRole
from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.interfaces.user_interface import IUserRepository
from src.infrastructure.config import settings


class AuthService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def admin_login(self, dto: AdminLoginDTO) -> TokenDTO:
        user = await self.user_repo.get_by_username(dto.username)
        if not user:
            raise NotFoundException("User", dto.username)
        if user.role != UserRole.ADMIN:
            raise ForbiddenException("Admin access required")
        if not user.phone:
            raise ForbiddenException("Admin account has no password set")
        if not self.verify_password(dto.password, user.phone):
            raise ForbiddenException("Invalid credentials")

        access_token = self._create_token(
            user_id=user.id,
            role=user.role,
            ttl=settings.JWT_ACCESS_TTL,
            token_type="access",
        )
        refresh_token = self._create_token(
            user_id=user.id,
            role=user.role,
            ttl=settings.JWT_REFRESH_TTL,
            token_type="refresh",
        )
        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> TokenDTO:
        payload = self.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ForbiddenException("Invalid refresh token")

        user_id = payload["sub"]
        user = await self.user_repo.get_by_id(int(user_id))
        if not user or user.role != UserRole.ADMIN:
            raise ForbiddenException("Invalid token")

        access_token = self._create_token(
            user_id=user.id,
            role=user.role,
            ttl=settings.JWT_ACCESS_TTL,
            token_type="access",
        )
        new_refresh = self._create_token(
            user_id=user.id,
            role=user.role,
            ttl=settings.JWT_REFRESH_TTL,
            token_type="refresh",
        )
        return TokenDTO(access_token=access_token, refresh_token=new_refresh)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ForbiddenException("Token expired")
        except jwt.InvalidTokenError:
            raise ForbiddenException("Invalid token")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def _create_token(*, user_id: int, role: str, ttl: int, token_type: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": token_type,
            "iat": now,
            "exp": now + timedelta(seconds=ttl),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
