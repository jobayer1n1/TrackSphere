from pydantic import BaseModel


class VehicleRead(BaseModel):
    id: int
    registration_number: str
    vehicle_type: str
    capacity: int
    status: str

    class Config:
        orm_mode = True
