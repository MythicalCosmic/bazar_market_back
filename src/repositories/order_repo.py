from datetime import datetime
from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from src.db.models.order import Order, OrderItem, OrderStatusLog
from src.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    async def get_by_order_number(self, order_number: str) -> Order | None:
        stmt = select(Order).where(Order.order_number == order_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int, *, offset: int = 0, limit: int = 50) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(self, status: str, *, offset: int = 0, limit: int = 100) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.status == status)
            .order_by(Order.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_orders(self, *, offset: int = 0, limit: int = 100) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.status.in_(["pending", "confirmed", "preparing", "delivering"]))
            .order_by(Order.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_items(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_full_details(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_log),
                selectinload(Order.payments),
            )
            .where(Order.id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, order_id: int, status: str, **timestamp_fields) -> bool:
        values: dict = {"status": status, **timestamp_fields}
        stmt = update(Order).where(Order.id == order_id).values(**values)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def update_payment_status(self, order_id: int, payment_status: str) -> bool:
        stmt = update(Order).where(Order.id == order_id).values(payment_status=payment_status)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(Order).where(Order.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one()


class OrderItemRepository(BaseRepository[OrderItem]):
    model = OrderItem

    async def get_by_order(self, order_id: int) -> Sequence[OrderItem]:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def bulk_create(self, items: list[dict]) -> list[OrderItem]:
        objs = [OrderItem(**item) for item in items]
        self.session.add_all(objs)
        await self.session.flush()
        return objs


class OrderStatusLogRepository(BaseRepository[OrderStatusLog]):
    model = OrderStatusLog

    async def get_by_order(self, order_id: int) -> Sequence[OrderStatusLog]:
        stmt = (
            select(OrderStatusLog)
            .where(OrderStatusLog.order_id == order_id)
            .order_by(OrderStatusLog.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def log_transition(
        self, order_id: int, from_status: str | None, to_status: str, *, changed_by: int | None = None, note: str | None = None
    ) -> OrderStatusLog:
        return await self.create(
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            note=note,
        )
