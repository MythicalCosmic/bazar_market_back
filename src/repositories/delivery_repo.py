from typing import Sequence

from sqlalchemy import select, update

from src.db.models.delivery import DeliveryZone
from src.repositories.base import BaseRepository


class DeliveryZoneRepository(BaseRepository[DeliveryZone]):
    model = DeliveryZone

    async def get_active(self) -> Sequence[DeliveryZone]:
        stmt = (
            select(DeliveryZone)
            .where(DeliveryZone.is_active.is_(True))
            .order_by(DeliveryZone.sort_order)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def deactivate(self, zone_id: int) -> bool:
        stmt = update(DeliveryZone).where(DeliveryZone.id == zone_id).values(is_active=False)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
