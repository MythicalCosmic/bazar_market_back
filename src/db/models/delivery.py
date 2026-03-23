from decimal import Decimal

from sqlalchemy import String, Integer, Boolean, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin


class DeliveryZone(TimestampMixin, Base):
    __tablename__ = "delivery_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    polygon: Mapped[dict] = mapped_column(JSONB, nullable=False)  
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_order: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<DeliveryZone {self.name} fee={self.delivery_fee}>"