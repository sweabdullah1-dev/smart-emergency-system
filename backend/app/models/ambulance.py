import enum
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AmbulanceStatus(str, enum.Enum):
    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    TRANSPORTING = "transporting"
    OFFLINE = "offline"


class Ambulance(Base):
    __tablename__ = "ambulances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plate_number: Mapped[str] = mapped_column(String(20), unique=True)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    lat: Mapped[float] = mapped_column(Float, default=24.7136)
    lng: Mapped[float] = mapped_column(Float, default=46.6753)
    status: Mapped[AmbulanceStatus] = mapped_column(SAEnum(AmbulanceStatus), default=AmbulanceStatus.AVAILABLE)
    city: Mapped[str] = mapped_column(String(100), default="Riyadh")
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver", back_populates="ambulance")
    emergencies = relationship("Emergency", back_populates="ambulance")
    gps_history = relationship("GPSTracking", back_populates="ambulance")
