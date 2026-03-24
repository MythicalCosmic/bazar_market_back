from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, BigInteger, Boolean, Index, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, SoftDeleteMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(String(100), unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="client")
    language: Mapped[str] = mapped_column(String(5), default="uz")
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    addresses: Mapped[list["Address"]] = relationship(back_populates="user", lazy="selectin")
    orders: Mapped[list["Order"]] = relationship(back_populates="user", lazy="noload")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user", lazy="noload")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", lazy="noload")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user", lazy="noload")

    __table_args__ = (
        Index("idx_users_role", "role"),
        Index("idx_users_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User {self.id} {self.first_name} ({self.role})>"


class Address(TimestampMixin, Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    address_text: Mapped[str] = mapped_column(Text, nullable=False)
    entrance: Mapped[str | None] = mapped_column(String(20))
    floor: Mapped[str | None] = mapped_column(String(10))
    apartment: Mapped[str | None] = mapped_column(String(20))
    comment: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="addresses")

    __table_args__ = (
        Index("idx_addresses_user", "user_id"),
        Index("idx_addresses_user_default", "user_id", "is_default"),
    )