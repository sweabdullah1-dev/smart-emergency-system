from datetime import datetime

from sqlalchemy import ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class GPSTracking(Base):
    __tablename__ = "gps_tracking"

    id: Mapped[int] = mapped_column(primary_key=True)
    ambulance_id: Mapped[int] = mapped_column(ForeignKey("ambulances.id"), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    speed_kmh: Mapped[float] = mapped_column(Float, default=0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ambulance = relationship("Ambulance", back_populates="gps_history")
