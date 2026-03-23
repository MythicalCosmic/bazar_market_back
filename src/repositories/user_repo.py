from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, update, func

from src.db.models.user import User, Address
from src.repositories.base import SoftDeleteRepository, BaseRepository


class UserRepository(SoftDeleteRepository[User]):
    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        stmt = select(User).where(User.phone == phone, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, code: str) -> User | None:
        stmt = select(User).where(User.referral_code == code, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_role(self, role: str, *, offset: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = (
            select(User)
            .where(User.role == role, User.deleted_at.is_(None))
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active(self, *, offset: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = (
            select(User)
            .where(User.is_active.is_(True), User.deleted_at.is_(None))
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def touch_last_seen(self, user_id: int) -> None:
        stmt = update(User).where(User.id == user_id).values(last_seen_at=func.now())
        await self.session.execute(stmt)
        await self.session.flush()

    async def adjust_balance(self, user_id: int, amount: Decimal) -> Decimal | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(balance=User.balance + amount)
            .returning(User.balance)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def deactivate(self, user_id: int) -> bool:
        stmt = update(User).where(User.id == user_id).values(is_active=False)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def get_by_user(self, user_id: int, *, active_only: bool = True) -> Sequence[Address]:
        stmt = select(Address).where(Address.user_id == user_id)
        if active_only:
            stmt = stmt.where(Address.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_default(self, user_id: int) -> Address | None:
        stmt = select(Address).where(
            Address.user_id == user_id,
            Address.is_default.is_(True),
            Address.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_default(self, user_id: int, address_id: int) -> None:
        await self.session.execute(
            update(Address).where(Address.user_id == user_id).values(is_default=False)
        )
        await self.session.execute(
            update(Address).where(Address.id == address_id, Address.user_id == user_id).values(is_default=True)
        )
        await self.session.flush()

    async def deactivate(self, address_id: int) -> bool:
        stmt = update(Address).where(Address.id == address_id).values(is_active=False)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
