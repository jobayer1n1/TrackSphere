from threading import Lock
from typing import Any
from sqlalchemy.orm import Session

from app.core.notifications.channels import InAppChannelAdapter, NotificationChannel
from app.core.notifications.decorators import InAppNotificationDecorator, PlainNotification
from app.core.tracking.service import Observer, tracking_subject
from app.models.enums import NotificationPriority, NotificationType


class NotificationService(Observer):
    """
    Singleton Pattern & Observer Pattern:
    NotificationService provides a centralized singleton for dispatching decorated notifications
    across registered channel adapters and automatically listens to telemetry/delivery events.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(NotificationService, cls).__new__(cls)
                    cls._instance._channels = [InAppChannelAdapter()]
                    # Register itself as an observer to GPSTrackingSubject
                    tracking_subject.attach(cls._instance)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "NotificationService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_channel(self, channel: NotificationChannel) -> None:
        self._channels.append(channel)

    def notify(
        self,
        db: Session,
        recipient_id: int,
        raw_message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        decorate: bool = True,
    ) -> None:
        """
        Decorate and dispatch notification to all active channels.
        """
        component = PlainNotification(raw_message)
        if decorate:
            component = InAppNotificationDecorator(component, priority_label=priority.value)

        formatted_message = component.get_formatted_message()

        for channel in self._channels:
            channel.send(
                db=db,
                recipient_id=recipient_id,
                message=formatted_message,
                notification_type=notification_type,
                priority=priority,
            )

    def update(self, event_type: str, data: dict[str, Any]) -> None:
        """Observer callback for tracking/system events."""
        # Logs or handles observer updates
        pass
