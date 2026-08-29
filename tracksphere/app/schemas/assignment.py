from datetime import datetime
from pydantic import BaseModel
from app.models.enums import AssignmentStatus
from app.schemas.driver import DriverRead
from app.schemas.vehicle import VehicleRead


class AssignmentBase(BaseModel):
    delivery_id: int
    driver_id: int
    vehicle_id: int | None = None


class AssignmentCreate(AssignmentBase):
    strategy: str | None = None



class AssignmentUpdate(BaseModel):
    status: AssignmentStatus | None = None
    driver_id: int | None = None
    vehicle_id: int | None = None


class AssignmentRead(AssignmentBase):
    id: int
    assigned_at: datetime
    status: AssignmentStatus
    driver: DriverRead | None = None
    vehicle: VehicleRead | None = None

    class Config:
        from_attributes = True
