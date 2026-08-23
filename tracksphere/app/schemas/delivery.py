from datetime import datetime
from pydantic import BaseModel
from app.models.enums import DeliveryStatus
from app.schemas.driver import DriverRead
from app.schemas.vehicle import VehicleRead


class DeliveryBase(BaseModel):
    pickup: str
    destination: str
    deadline: datetime
    priority: int = 2
    notes: str | None = None


class DeliveryCreate(DeliveryBase):
    driver_id: int | None = None
    vehicle_id: int | None = None


class DeliveryUpdate(BaseModel):
    pickup: str | None = None
    destination: str | None = None
    deadline: datetime | None = None
    priority: int | None = None
    status: DeliveryStatus | None = None
    driver_id: int | None = None
    vehicle_id: int | None = None
    notes: str | None = None


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus


class DeliveryRead(DeliveryBase):
    id: int
    status: DeliveryStatus
    driver_id: int | None = None
    vehicle_id: int | None = None
    created_at: datetime
    updated_at: datetime
    driver: DriverRead | None = None
    vehicle: VehicleRead | None = None

    class Config:
        from_attributes = True
