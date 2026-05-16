from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Citizen(Base):
    __tablename__ = "citizens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    default_lat: Mapped[float | None] = mapped_column(nullable=True)
    default_lng: Mapped[float | None] = mapped_column(nullable=True)

    user = relationship("User", back_populates="citizen")
    emergencies = relationship("Emergency", back_populates="citizen")
