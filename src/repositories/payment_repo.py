from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from src.db.models.payment import Payment, PaymentStatusLog, Coupon, CouponUsage
from src.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def get_by_order(self, order_id: int) -> Sequence[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_external_id(self, external_id: str) -> Payment | None:
        stmt = select(Payment).where(Payment.external_id == external_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str, *, offset: int = 0, limit: int = 100) -> Sequence[Payment]:
        stmt = select(Payment).where(Payment.status == status).order_by(Payment.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_log(self, payment_id: int) -> Payment | None:
        stmt = (
            select(Payment)
            .options(selectinload(Payment.status_log))
            .where(Payment.id == payment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_paid(self, payment_id: int, external_id: str | None = None) -> bool:
        values: dict = {"status": "paid", "paid_at": func.now()}
        if external_id:
            values["external_id"] = external_id
        stmt = update(Payment).where(Payment.id == payment_id).values(**values)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def mark_failed(self, payment_id: int, error_message: str) -> bool:
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id)
            .values(status="failed", failed_at=func.now(), error_message=error_message)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def mark_refunded(self, payment_id: int, refund_amount: Decimal, reason: str) -> bool:
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id)
            .values(status="refunded", refund_amount=refund_amount, refund_reason=reason, refunded_at=func.now())
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0


class PaymentStatusLogRepository(BaseRepository[PaymentStatusLog]):
    model = PaymentStatusLog

    async def get_by_payment(self, payment_id: int) -> Sequence[PaymentStatusLog]:
        stmt = (
            select(PaymentStatusLog)
            .where(PaymentStatusLog.payment_id == payment_id)
            .order_by(PaymentStatusLog.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def log_transition(
        self, payment_id: int, from_status: str | None, to_status: str,
        *, note: str | None = None, provider_data: dict | None = None,
    ) -> PaymentStatusLog:
        return await self.create(
            payment_id=payment_id,
            from_status=from_status,
            to_status=to_status,
            note=note,
            provider_data=provider_data,
        )


class CouponRepository(BaseRepository[Coupon]):
    model = Coupon

    async def get_by_code(self, code: str) -> Coupon | None:
        stmt = select(Coupon).where(Coupon.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(self) -> Sequence[Coupon]:
        now = func.now()
        stmt = (
            select(Coupon)
            .where(
                Coupon.is_active.is_(True),
                (Coupon.starts_at.is_(None) | (Coupon.starts_at <= now)),
                (Coupon.expires_at.is_(None) | (Coupon.expires_at >= now)),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_valid_for_user(self, code: str, user_id: int) -> Coupon | None:
        now = func.now()
        stmt = (
            select(Coupon)
            .where(
                Coupon.code == code,
                Coupon.is_active.is_(True),
                (Coupon.starts_at.is_(None) | (Coupon.starts_at <= now)),
                (Coupon.expires_at.is_(None) | (Coupon.expires_at >= now)),
                (Coupon.usage_limit.is_(None) | (Coupon.used_count < Coupon.usage_limit)),
            )
        )
        result = await self.session.execute(stmt)
        coupon = result.scalar_one_or_none()
        if not coupon:
            return None

        usage_count = await self.session.execute(
            select(func.count())
            .select_from(CouponUsage)
            .where(CouponUsage.coupon_id == coupon.id, CouponUsage.user_id == user_id)
        )
        if usage_count.scalar_one() >= coupon.per_user_limit:
            return None

        return coupon

    async def increment_usage(self, coupon_id: int) -> None:
        stmt = update(Coupon).where(Coupon.id == coupon_id).values(used_count=Coupon.used_count + 1)
        await self.session.execute(stmt)
        await self.session.flush()


class CouponUsageRepository(BaseRepository[CouponUsage]):
    model = CouponUsage

    async def get_by_coupon(self, coupon_id: int) -> Sequence[CouponUsage]:
        stmt = select(CouponUsage).where(CouponUsage.coupon_id == coupon_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user(self, user_id: int) -> Sequence[CouponUsage]:
        stmt = select(CouponUsage).where(CouponUsage.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def user_usage_count(self, coupon_id: int, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(CouponUsage)
            .where(CouponUsage.coupon_id == coupon_id, CouponUsage.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
