from __future__ import annotations
from typing import Optional

from .events import (
    DeliveryAssignedEvent,
    DeliveryCompletedEvent,
    DeliveryCancelledEvent,
    DeliveryStatusChangedEvent,
    DeliveryEvent,
)
from .observer import Observer
from tracksphere.app.models import Notification, NotificationPriority, NotificationType, User
from tracksphere.app.repositories.notification_repository import NotificationRepository


class NotificationObserver(Observer):
    def __init__(self, notification_repository: NotificationRepository, recipient: User):
        self.notification_repository = notification_repository
        self.recipient = recipient

    def update(self, event: DeliveryAssignedEvent | DeliveryStatusChangedEvent | DeliveryCompletedEvent | DeliveryCancelledEvent) -> None:
        message = self._build_message(event)
        notification = Notification(
            recipient_id=self.recipient.id,
            message=message,
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
            read=False,
        )
        self.notification_repository.create(notification)

    @staticmethod
    def _build_message(event: DeliveryEvent) -> str:
        if isinstance(event, DeliveryAssignedEvent):
            return f"Delivery {event.delivery_id} assigned to driver {event.driver_id}."
        if isinstance(event, DeliveryCompletedEvent):
            return f"Delivery {event.delivery_id} completed."
        if isinstance(event, DeliveryCancelledEvent):
            return f"Delivery {event.delivery_id} cancelled."
        if isinstance(event, DeliveryStatusChangedEvent):
            return f"Delivery {event.delivery_id} status changed from {event.previous_status.value} to {event.new_status.value}."
        return f"Delivery {event.delivery_id} event: {event.event_type}."


class DashboardObserver(Observer):
    def __init__(self):
        self.events: list[DeliveryEvent] = []

    def update(self, event: DeliveryAssignedEvent | DeliveryStatusChangedEvent | DeliveryCompletedEvent | DeliveryCancelledEvent) -> None:
        self.events.append(event)

    def latest_event(self) -> Optional[DeliveryEvent]:
        return self.events[-1] if self.events else None
