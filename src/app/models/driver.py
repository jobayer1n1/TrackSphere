from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AvailabilityStatus


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    license_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    availability: Mapped[AvailabilityStatus] = mapped_column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="driver")
    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates="driver")
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="driver")
