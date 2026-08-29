from datetime import datetime
from pydantic import BaseModel


class LocationCreate(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    timestamp: datetime | None = None


class LocationRead(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        from_attributes = True


class DriverLocationRead(BaseModel):
    driver_id: int
    driver_name: str | None = None
    vehicle_id: int
    vehicle_registration: str | None = None
    latitude: float
    longitude: float
    timestamp: datetime


class LocationSearchResult(BaseModel):
    target_type: str  # "vehicle" or "driver"
    target_id: int
    title: str
    subtitle: str
    is_assigned: bool = True
    vehicle_id: int | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str | None = None
    message: str | None = None

