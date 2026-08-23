from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.models.enums import NotificationPriority, NotificationType
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationChannel(ABC):
    """
    Target Interface for Notification Channels (Adapter Pattern).
    """

    @abstractmethod
    def send(
        self,
        db: Session | None,
        recipient_id: int,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
    ) -> bool:
        raise NotImplementedError


class InAppChannelAdapter(NotificationChannel):
    """
    Adapter Pattern:
    Adapts notification delivery to SQLite database persistence for in-app alert feeds.
    """

    def send(
        self,
        db: Session | None,
        recipient_id: int,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> bool:
        if not db:
            return False

        repo = NotificationRepository(db)
        notification = Notification(
            recipient_id=recipient_id,
            message=message,
            notification_type=notification_type,
            priority=priority,
            read=False,
        )
        repo.create(notification)
        return True


class ExternalChannelAdapter(NotificationChannel):
    """
    Adapter Pattern:
    Adapts notification delivery to external logging or mock external webhook services.
    """

    def __init__(self, endpoint_name: str = "Dispatch-Webhook"):
        self.endpoint_name = endpoint_name

    def send(
        self,
        db: Session | None,
        recipient_id: int,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> bool:
        print(
            f"[{self.endpoint_name}] External notification to User {recipient_id} [{priority.value}]: {message}"
        )
        return True
