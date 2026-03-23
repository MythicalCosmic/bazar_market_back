from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String, Integer, Boolean, Numeric, ForeignKey, Index, DateTime, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin


class Payment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)  # click, payme, cash
    external_id: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(5), nullable=False, default="UZS")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    provider_data: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refund_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    refund_reason: Mapped[str | None] = mapped_column(Text)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order: Mapped["Order"] = relationship(back_populates="payments")
    status_log: Mapped[list["PaymentStatusLog"]] = relationship(
        back_populates="payment", lazy="noload", order_by="PaymentStatusLog.created_at"
    )

    __table_args__ = (
        Index("idx_payments_order", "order_id"),
        Index("idx_payments_external", "external_id"),
        Index("idx_payments_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Payment {self.id} {self.method} {self.amount} [{self.status}]>"


class PaymentStatusLog(Base):
    __tablename__ = "payment_status_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    provider_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    payment: Mapped["Payment"] = relationship(back_populates="status_log")

    __table_args__ = (
        Index("idx_payment_status_log_payment", "payment_id"),
        Index("idx_payment_status_log_created", "created_at"),
    )


class Coupon(TimestampMixin, Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False) 
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_order: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    max_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    usage_limit: Mapped[int | None] = mapped_column(Integer)
    per_user_limit: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    usages: Mapped[list["CouponUsage"]] = relationship(back_populates="coupon", lazy="noload")

    __table_args__ = (
        Index("idx_coupons_code", "code"),
        Index("idx_coupons_active", "is_active", "starts_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<Coupon {self.code} ({self.type}: {self.value})>"


class CouponUsage(Base):
    __tablename__ = "coupon_usages"

    id: Mapped[int] = mapped_column(primary_key=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    coupon: Mapped["Coupon"] = relationship(back_populates="usages")
    user: Mapped["User"] = relationship(lazy="joined")
    order: Mapped["Order"] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_coupon_usage_coupon_user", "coupon_id", "user_id"),
    )