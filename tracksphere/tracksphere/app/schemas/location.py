from datetime import datetime
from pydantic import BaseModel


class LocationUpdatePayload(BaseModel):
    vehicle_id: str | int | None = None
    latitude: float
    longitude: float
    accuracy: float | None = None
    altitude: float | None = None
    speed: float | None = None
    timestamp: datetime | str | None = None


class LocationRead(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        from_attributes = True
        orm_mode = True

