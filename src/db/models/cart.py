from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, DateTime, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        Index("idx_cart_user", "user_id"),
    )