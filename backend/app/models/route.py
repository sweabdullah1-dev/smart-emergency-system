from datetime import datetime

from sqlalchemy import ForeignKey, Text, Float, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    emergency_id: Mapped[int] = mapped_column(ForeignKey("emergencies.id"))
    algorithm: Mapped[str] = mapped_column(String(20), default="astar")
    polyline: Mapped[str | None] = mapped_column(Text, nullable=True)
    distance_km: Mapped[float] = mapped_column(Float, default=0)
    eta_minutes: Mapped[float] = mapped_column(Float, default=0)
    waypoints_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    emergency = relationship("Emergency", back_populates="routes")
