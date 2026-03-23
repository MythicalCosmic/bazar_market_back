from datetime import datetime

from sqlalchemy import String, Integer, Text, ForeignKey, Index, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # create, update, delete
    entity: Mapped[str] = mapped_column(String(50), nullable=False)  # product, order, user, etc.
    entity_id: Mapped[int | None] = mapped_column(Integer)
    old_data: Mapped[dict | None] = mapped_column(JSONB)
    new_data: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User | None"] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_audit_log_user", "user_id"),
        Index("idx_audit_log_entity", "entity", "entity_id"),
        Index("idx_audit_log_action", "action"),
        Index("idx_audit_log_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.entity}:{self.entity_id} by user:{self.user_id}>"
