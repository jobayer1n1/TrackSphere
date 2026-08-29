from datetime import datetime
from pydantic import BaseModel
from app.models.enums import NotificationPriority, NotificationType


class NotificationBase(BaseModel):
    message: str
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.MEDIUM


class NotificationCreate(NotificationBase):
    recipient_id: int


class NotificationRead(NotificationBase):
    id: int
    recipient_id: int
    read: bool
    timestamp: datetime

    class Config:
        from_attributes = True
