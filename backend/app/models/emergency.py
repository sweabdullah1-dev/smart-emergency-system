import enum
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, Text, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EmergencyType(str, enum.Enum):
    CARDIAC = "cardiac"
    TRAUMA = "trauma"
    RESPIRATORY = "respiratory"
    STROKE = "stroke"
    ACCIDENT = "accident"
    FIRE_RELATED = "fire_related"
    OTHER = "other"


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmergencyStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    PICKED_UP = "picked_up"
    TRANSPORTING = "transporting"
    ARRIVED_HOSPITAL = "arrived_hospital"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Emergency(Base):
    __tablename__ = "emergencies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    citizen_id: Mapped[int | None] = mapped_column(ForeignKey("citizens.id"), nullable=True)
    reporter_name: Mapped[str] = mapped_column(String(255))
    reporter_phone: Mapped[str] = mapped_column(String(50))
    emergency_type: Mapped[EmergencyType] = mapped_column(SAEnum(EmergencyType))
    severity: Mapped[SeverityLevel] = mapped_column(SAEnum(SeverityLevel))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EmergencyStatus] = mapped_column(SAEnum(EmergencyStatus), default=EmergencyStatus.PENDING)
    ambulance_id: Mapped[int | None] = mapped_column(ForeignKey("ambulances.id"), nullable=True)
    hospital_id: Mapped[int | None] = mapped_column(ForeignKey("hospitals.id"), nullable=True)
    eta_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    route_polyline: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_score: Mapped[int] = mapped_column(Integer, default=0)
    auto_assigned: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    citizen = relationship("Citizen", back_populates="emergencies")
    ambulance = relationship("Ambulance", back_populates="emergencies")
    hospital = relationship("Hospital", back_populates="emergencies")
    routes = relationship("Route", back_populates="emergency")
    status_logs = relationship("StatusLog", back_populates="emergency")
    notifications = relationship("Notification", back_populates="emergency")
