from datetime import datetime
from sqlalchemy import String, Boolean, Text, ForeignKey, Index, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  
    title: Mapped[str | None] = mapped_column(String(300))
    body: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSONB)  
    channel: Mapped[str] = mapped_column(String(20), nullable=False) 
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_notifications_user_read", "user_id", "is_read"),
        Index("idx_notifications_sent", "sent_at"),
    )