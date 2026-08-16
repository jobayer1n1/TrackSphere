from datetime import datetime
from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    recipient_id: int
    message: str
    notification_type: str
    priority: str
    read: bool
    timestamp: datetime

    class Config:
        orm_mode = True
