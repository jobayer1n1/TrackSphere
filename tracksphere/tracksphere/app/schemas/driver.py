from pydantic import BaseModel


class DriverRead(BaseModel):
    id: int
    user_id: int
    license_number: str
    availability: str

    class Config:
        orm_mode = True
