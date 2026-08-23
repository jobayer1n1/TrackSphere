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
