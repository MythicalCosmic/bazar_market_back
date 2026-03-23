from typing import Sequence

from sqlalchemy import select

from src.db.models.audit import AuditLog
from src.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def log(
        self, action: str, entity: str, *,
        entity_id: int | None = None,
        user_id: int | None = None,
        old_data: dict | None = None,
        new_data: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        return await self.create(
            action=action,
            entity=entity,
            entity_id=entity_id,
            user_id=user_id,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
        )

    async def get_by_entity(self, entity: str, entity_id: int, *, offset: int = 0, limit: int = 50) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.entity == entity, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user(self, user_id: int, *, offset: int = 0, limit: int = 50) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_action(self, action: str, *, offset: int = 0, limit: int = 50) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
