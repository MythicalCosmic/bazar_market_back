
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String, Integer, Boolean, Text, Numeric, ForeignKey, Index, DateTime,
    UniqueConstraint, CheckConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="favorites")
    product: Mapped["Product"] = relationship(lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_favorite_user_product"),
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="reviews")
    order: Mapped["Order"] = relationship(lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "order_id", name="uq_review_user_order"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        Index("idx_reviews_order", "order_id"),
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reward_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    referrer: Mapped["User"] = relationship(foreign_keys=[referrer_id], lazy="joined")
    referred: Mapped["User"] = relationship(foreign_keys=[referred_id], lazy="joined")

    __table_args__ = (
        UniqueConstraint("referred_id", name="uq_referral_referred"),
        Index("idx_referrals_referrer", "referrer_id"),
    )