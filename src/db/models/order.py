from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String, Integer, Boolean, Text, Numeric, ForeignKey, Index, DateTime, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base, TimestampMixin, UUIDMixin


class Order(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    coupon_id: Mapped[int | None] = mapped_column(ForeignKey("coupons.id"))
    delivery_zone_id: Mapped[int | None] = mapped_column(ForeignKey("delivery_zones.id"))

    payment_method: Mapped[str | None] = mapped_column(String(20))  # cash, click, payme
    payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")

    address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id"))
    delivery_address_text: Mapped[str | None] = mapped_column(Text)
    delivery_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    delivery_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user_note: Mapped[str | None] = mapped_column(Text)
    admin_note: Mapped[str | None] = mapped_column(Text)
    cancel_reason: Mapped[str | None] = mapped_column(Text)

    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="orders", lazy="joined")
    address: Mapped["Address | None"] = relationship(lazy="joined")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", lazy="selectin", order_by="OrderItem.id"
    )
    status_log: Mapped[list["OrderStatusLog"]] = relationship(
        back_populates="order", lazy="noload", order_by="OrderStatusLog.created_at"
    )
    coupon: Mapped["Coupon | None"] = relationship(lazy="joined")
    delivery_zone: Mapped["DeliveryZone | None"] = relationship(lazy="joined")
    payments: Mapped[list["Payment"]] = relationship(back_populates="order", lazy="noload")

    __table_args__ = (
        Index("idx_orders_user", "user_id"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_created", "created_at"),
        Index("idx_orders_active", "status", "created_at"),
        Index("idx_orders_user_history", "user_id", "created_at"),
        Index("idx_orders_daily_analytics", "created_at", "status"),
    )

    def __repr__(self) -> str:
        return f"<Order {self.order_number} [{self.status}] {self.total}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    product_name: Mapped[str] = mapped_column(String(300), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_order_items_order", "order_id"),
        Index("idx_order_items_product", "product_id"),
    )


class OrderStatusLog(Base):
    __tablename__ = "order_status_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="status_log")
    changed_by_user: Mapped["User | None"] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_status_log_order", "order_id"),
        Index("idx_status_log_created", "created_at"),
    )