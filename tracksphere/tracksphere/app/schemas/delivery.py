from datetime import datetime
from pydantic import BaseModel


class DeliveryRead(BaseModel):
    id: int
    pickup: str
    destination: str
    deadline: datetime
    priority: int
    status: str
    driver_id: int | None
    vehicle_id: int | None
    notes: str | None

    class Config:
        orm_mode = True
