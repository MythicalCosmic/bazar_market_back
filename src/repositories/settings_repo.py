from typing import Sequence

from sqlalchemy import select, update

from src.db.models.settings import Setting
from src.repositories.base import BaseRepository


class SettingRepository(BaseRepository[Setting]):
    model = Setting

    async def get_by_key(self, key: str) -> Setting | None:
        stmt = select(Setting).where(Setting.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_value(self, key: str, default: str | None = None) -> str | None:
        setting = await self.get_by_key(key)
        return setting.value if setting else default

    async def set_value(self, key: str, value: str, description: str | None = None) -> Setting:
        existing = await self.get_by_key(key)
        if existing:
            existing.value = value
            if description is not None:
                existing.description = description
            await self.session.flush()
            return existing
        return await self.create(key=key, value=value, description=description)

    async def get_all_as_dict(self) -> dict[str, str]:
        stmt = select(Setting)
        result = await self.session.execute(stmt)
        return {s.key: s.value for s in result.scalars().all()}
