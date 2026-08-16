from datetime import datetime

from app.application.notifications import (
    DashboardObserver,
    DeliveryAssignedEvent,
    DeliveryCancelledEvent,
    DeliveryEventSource,
    DeliveryStatusChangedEvent,
    NotificationObserver,
)
from app.models import Notification, NotificationPriority, NotificationType, User


class DummyNotificationRepository:
    def __init__(self):
        self.notifications: list[Notification] = []

    def create(self, notification: Notification) -> Notification:
        self.notifications.append(notification)
        notification.id = len(self.notifications)
        return notification


def test_subject_attach_notify_detach():
    subject = DeliveryEventSource()
    observer = DashboardObserver()

    subject.attach(observer)
    assert subject._observers == [observer]

    event = DeliveryAssignedEvent(
        delivery_id=1,
        timestamp=datetime.utcnow(),
        event_type="assigned",
        details="Assigned",
        driver_id=1,
        vehicle_id=None,
    )
    subject.notify(event)

    assert observer.latest_event() == event

    subject.detach(observer)
    subject.notify(event)
    assert observer.latest_event() == event


def test_multiple_observers_receive_events():
    subject = DeliveryEventSource()
    dashboard = DashboardObserver()
    repo = DummyNotificationRepository()
    recipient = User(id=1, name="Dispatcher", email="disp@example.com", password_hash="pw", role="DISPATCHER", active=True)
    notification_observer = NotificationObserver(repo, recipient)

    subject.attach(dashboard)
    subject.attach(notification_observer)

    event = DeliveryCancelledEvent(
        delivery_id=2,
        timestamp=datetime.utcnow(),
        event_type="cancelled",
        details="Cancelled by dispatcher",
        previous_status="ASSIGNED",
        new_status="CANCELLED",
    )
    subject.notify(event)

    assert dashboard.latest_event() == event
    assert len(repo.notifications) == 1
    assert repo.notifications[0].message == "Delivery 2 cancelled."
    assert repo.notifications[0].notification_type == NotificationType.INFO
    assert repo.notifications[0].priority == NotificationPriority.MEDIUM
