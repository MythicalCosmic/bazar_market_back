from datetime import date
from typing import Sequence

from sqlalchemy import select, func

from src.db.models.analytics import DailyStat, SearchLog
from src.repositories.base import BaseRepository


class DailyStatRepository(BaseRepository[DailyStat]):
    model = DailyStat

    async def get_by_date(self, d: date) -> DailyStat | None:
        stmt = select(DailyStat).where(DailyStat.date == d)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_range(self, start: date, end: date) -> Sequence[DailyStat]:
        stmt = (
            select(DailyStat)
            .where(DailyStat.date >= start, DailyStat.date <= end)
            .order_by(DailyStat.date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def upsert(self, d: date, **kwargs) -> DailyStat:
        existing = await self.get_by_date(d)
        if existing:
            for k, v in kwargs.items():
                setattr(existing, k, v)
            await self.session.flush()
            return existing
        return await self.create(date=d, **kwargs)


class SearchLogRepository(BaseRepository[SearchLog]):
    model = SearchLog

    async def log_search(self, query: str, results_count: int, user_id: int | None = None) -> SearchLog:
        return await self.create(query=query, results_count=results_count, user_id=user_id)

    async def top_queries(self, *, limit: int = 20) -> Sequence[tuple[str, int]]:
        stmt = (
            select(SearchLog.query, func.count().label("cnt"))
            .group_by(SearchLog.query)
            .order_by(func.count().desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_by_user(self, user_id: int, *, limit: int = 50) -> Sequence[SearchLog]:
        stmt = (
            select(SearchLog)
            .where(SearchLog.user_id == user_id)
            .order_by(SearchLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
