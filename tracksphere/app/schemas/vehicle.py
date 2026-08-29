from datetime import datetime
from pydantic import BaseModel
from app.models.enums import VehicleStatus


class VehicleBase(BaseModel):
    registration_number: str
    vehicle_type: str
    capacity: int
    status: VehicleStatus = VehicleStatus.AVAILABLE


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    registration_number: str | None = None
    vehicle_type: str | None = None
    capacity: int | None = None
    status: VehicleStatus | None = None


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
