from typing import Sequence

from sqlalchemy import select, update, func

from src.db.models.notification import Notification
from src.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    async def get_by_user(self, user_id: int, *, offset: int = 0, limit: int = 50) -> Sequence[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.sent_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_unread(self, user_id: int) -> Sequence[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .order_by(Notification.sent_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def unread_count(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def mark_read(self, notification_id: int) -> bool:
        stmt = update(Notification).where(Notification.id == notification_id).values(is_read=True)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def mark_all_read(self, user_id: int) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def get_by_type(self, user_id: int, type: str) -> Sequence[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.type == type)
            .order_by(Notification.sent_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
