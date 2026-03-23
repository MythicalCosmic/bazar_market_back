from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Integer, Date, Numeric, ForeignKey, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class DailyStat(Base):
    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    avg_order_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    top_product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    top_product: Mapped["Product | None"] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_daily_stats_date", "date", unique=True),
    )


class SearchLog(Base):
    __tablename__ = "search_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    query: Mapped[str] = mapped_column(String(300), nullable=False)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_search_logs_created", "created_at"),
        Index("idx_search_logs_query", "query"),
    )