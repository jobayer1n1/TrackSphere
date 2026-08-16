from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from tracksphere.app.models import Notification, NotificationPriority, NotificationType, User


class NotificationComponent(ABC):
    @abstractmethod
    def get_recipient(self) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_message(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_type(self) -> NotificationType:
        raise NotImplementedError

    @abstractmethod
    def get_priority(self) -> NotificationPriority:
        raise NotImplementedError

    @abstractmethod
    def get_timestamp(self) -> datetime:
        raise NotImplementedError

    @abstractmethod
    def build(self) -> Notification:
        raise NotImplementedError


class BasicNotification(NotificationComponent):
    def __init__(
        self,
        recipient: User,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        timestamp: datetime | None = None,
    ):
        self._recipient = recipient
        self._message = message
        self._type = notification_type
        self._priority = priority
        self._timestamp = timestamp or datetime.utcnow()

    def get_recipient(self) -> User:
        return self._recipient

    def get_message(self) -> str:
        return self._message

    def get_type(self) -> NotificationType:
        return self._type

    def get_priority(self) -> NotificationPriority:
        return self._priority

    def get_timestamp(self) -> datetime:
        return self._timestamp

    def build(self) -> Notification:
        return Notification(
            recipient_id=self._recipient.id,
            message=self._message,
            notification_type=self._type,
            priority=self._priority,
            read=False,
            timestamp=self._timestamp,
        )


class NotificationDecorator(NotificationComponent):
    def __init__(self, component: NotificationComponent):
        self._component = component

    def get_recipient(self) -> User:
        return self._component.get_recipient()

    def get_message(self) -> str:
        return self._component.get_message()

    def get_type(self) -> NotificationType:
        return self._component.get_type()

    def get_priority(self) -> NotificationPriority:
        return self._component.get_priority()

    def get_timestamp(self) -> datetime:
        return self._component.get_timestamp()

    def build(self) -> Notification:
        return self._component.build()


class PriorityDecorator(NotificationDecorator):
    def __init__(self, component: NotificationComponent, priority: NotificationPriority):
        super().__init__(component)
        self._priority = priority

    def get_priority(self) -> NotificationPriority:
        return self._priority

    def build(self) -> Notification:
        base = self._component.build()
        base.priority = self._priority
        return base


class TimestampDecorator(NotificationDecorator):
    def __init__(self, component: NotificationComponent, timestamp: datetime | None = None):
        super().__init__(component)
        self._timestamp = timestamp or datetime.utcnow()

    def get_timestamp(self) -> datetime:
        return self._timestamp

    def build(self) -> Notification:
        base = self._component.build()
        base.timestamp = self._timestamp
        return base


class LoggingDecorator(NotificationDecorator):
    def get_message(self) -> str:
        original = super().get_message()
        return f"[LOGGED] {original}"

    def build(self) -> Notification:
        notification = super().build()
        notification.message = self.get_message()
        return notification
