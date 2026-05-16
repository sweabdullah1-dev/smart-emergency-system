from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class StatusLog(Base):
    __tablename__ = "status_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    emergency_id: Mapped[int] = mapped_column(ForeignKey("emergencies.id"))
    status: Mapped[str] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    emergency = relationship("Emergency", back_populates="status_logs")
