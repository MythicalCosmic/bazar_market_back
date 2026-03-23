from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, delete, update, func

from src.db.models.social import Favorite, Review, Referral
from src.repositories.base import BaseRepository


class FavoriteRepository(BaseRepository[Favorite]):
    model = Favorite

    async def get_by_user(self, user_id: int) -> Sequence[Favorite]:
        stmt = select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def is_favorited(self, user_id: int, product_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(Favorite)
            .where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def toggle(self, user_id: int, product_id: int) -> bool:
        existing = await self.session.execute(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        )
        fav = existing.scalar_one_or_none()
        if fav:
            await self.session.delete(fav)
            await self.session.flush()
            return False
        await self.create(user_id=user_id, product_id=product_id)
        return True

    async def favorite_count(self, product_id: int) -> int:
        stmt = select(func.count()).select_from(Favorite).where(Favorite.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()


class ReviewRepository(BaseRepository[Review]):
    model = Review

    async def get_by_order(self, order_id: int) -> Review | None:
        stmt = select(Review).where(Review.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int, *, offset: int = 0, limit: int = 50) -> Sequence[Review]:
        stmt = (
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def average_rating(self) -> float | None:
        stmt = select(func.avg(Review.rating))
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        return round(float(val), 2) if val else None


class ReferralRepository(BaseRepository[Referral]):
    model = Referral

    async def get_by_referrer(self, referrer_id: int) -> Sequence[Referral]:
        stmt = select(Referral).where(Referral.referrer_id == referrer_id).order_by(Referral.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_referred(self, referred_id: int) -> Referral | None:
        stmt = select(Referral).where(Referral.referred_id == referred_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_rewarded(self, referral_id: int) -> bool:
        stmt = update(Referral).where(Referral.id == referral_id).values(is_rewarded=True)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def referral_count(self, referrer_id: int) -> int:
        stmt = select(func.count()).select_from(Referral).where(Referral.referrer_id == referrer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def total_rewards(self, referrer_id: int) -> Decimal:
        stmt = (
            select(func.coalesce(func.sum(Referral.reward_amount), 0))
            .where(Referral.referrer_id == referrer_id, Referral.is_rewarded.is_(True))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
