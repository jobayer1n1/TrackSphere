from datetime import datetime
from pydantic import BaseModel
from app.models.enums import AvailabilityStatus
from app.schemas.user import UserRead


class DriverBase(BaseModel):
    license_number: str
    availability: AvailabilityStatus = AvailabilityStatus.AVAILABLE


class DriverCreate(DriverBase):
    user_id: int


class DriverUpdate(BaseModel):
    license_number: str | None = None
    availability: AvailabilityStatus | None = None


class DriverRead(DriverBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserRead | None = None

    class Config:
        from_attributes = True
