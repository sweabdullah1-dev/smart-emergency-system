import enum

from sqlalchemy import String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TrafficLevel(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class TrafficZone(Base):
    __tablename__ = "traffic_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    center_lat: Mapped[float] = mapped_column(Float)
    center_lng: Mapped[float] = mapped_column(Float)
    radius_km: Mapped[float] = mapped_column(Float, default=2.0)
    level: Mapped[TrafficLevel] = mapped_column(SAEnum(TrafficLevel), default=TrafficLevel.GREEN)
  # speed multiplier: green=1.0, yellow=0.7, red=0.4
    speed_factor: Mapped[float] = mapped_column(Float, default=1.0)
