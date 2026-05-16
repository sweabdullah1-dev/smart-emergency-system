import enum
from sqlalchemy import String, Float, Integer, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class HospitalType(str, enum.Enum):
    GENERAL = "general"
    TRAUMA = "trauma"
    SPECIALTY = "specialty"
    UNIVERSITY = "university"


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    name_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    capacity: Mapped[int] = mapped_column(Integer, default=100)
    current_load: Mapped[int] = mapped_column(Integer, default=0)
    emergency_available: Mapped[bool] = mapped_column(Boolean, default=True)
    hospital_type: Mapped[HospitalType] = mapped_column(SAEnum(HospitalType), default=HospitalType.GENERAL)
    user_id: Mapped[int | None] = mapped_column(nullable=True)

    emergencies = relationship("Emergency", back_populates="hospital")
