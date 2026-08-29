from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import VehicleStatus


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registration_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(64), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates="vehicle")
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="vehicle")
    locations: Mapped[list["Location"]] = relationship("Location", back_populates="vehicle", cascade="all, delete-orphan")
