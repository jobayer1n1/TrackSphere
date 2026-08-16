from datetime import datetime

from app.application.facades.delivery_management_facade import DeliveryManagementFacade
from app.application.notifications.notification_decorator import (
    BasicNotification,
    LoggingDecorator,
    PriorityDecorator,
    TimestampDecorator,
)
from app.models import NotificationPriority, NotificationType, User
from app.models import Driver


def test_basic_notification_builds_notification():
    user = User(id=1, name="Test", email="test@example.com", password_hash="pw", role="DISPATCHER", active=True)
    notification = BasicNotification(
        recipient=user,
        message="Hello",
        notification_type=NotificationType.INFO,
        priority=NotificationPriority.MEDIUM,
    )

    built = notification.build()

    assert built.recipient_id == user.id
    assert built.message == "Hello"
    assert built.notification_type == NotificationType.INFO
    assert built.priority == NotificationPriority.MEDIUM
    assert built.timestamp is not None


def test_priority_decorator_overrides_priority():
    user = User(id=1, name="Test", email="test@example.com", password_hash="pw", role="DISPATCHER", active=True)
    notification = BasicNotification(
        recipient=user,
        message="Hello",
        priority=NotificationPriority.MEDIUM,
    )
    decorated = PriorityDecorator(notification, NotificationPriority.HIGH)
    built = decorated.build()

    assert built.priority == NotificationPriority.HIGH
    assert notification.get_priority() == NotificationPriority.MEDIUM


def test_timestamp_decorator_sets_timestamp():
    user = User(id=1, name="Test", email="test@example.com", password_hash="pw", role="DISPATCHER", active=True)
    notification = BasicNotification(
        recipient=user,
        message="Hello",
        priority=NotificationPriority.MEDIUM,
    )
    timestamp = datetime(2026, 1, 1)
    decorated = TimestampDecorator(notification, timestamp)
    built = decorated.build()

    assert built.timestamp == timestamp
    assert notification.get_timestamp() != timestamp


def test_multiple_decorators_are_composable():
    user = User(id=1, name="Test", email="test@example.com", password_hash="pw", role="DISPATCHER", active=True)
    notification = BasicNotification(
        recipient=user,
        message="Hello",
        priority=NotificationPriority.MEDIUM,
    )
    wrapped = PriorityDecorator(notification, NotificationPriority.LOW)
    wrapped = TimestampDecorator(wrapped, datetime(2026, 1, 1))
    wrapped = LoggingDecorator(wrapped)

    built = wrapped.build()

    assert built.priority == NotificationPriority.LOW
    assert built.message.startswith("[LOGGED]")
    assert built.timestamp == datetime(2026, 1, 1)


def test_original_notification_remains_usable_after_decorators():
    user = User(id=1, name="Test", email="test@example.com", password_hash="pw", role="DISPATCHER", active=True)
    notification = BasicNotification(
        recipient=user,
        message="Hello",
        priority=NotificationPriority.MEDIUM,
    )
    wrapped = PriorityDecorator(notification, NotificationPriority.HIGH)
    wrapped.build()

    assert notification.get_priority() == NotificationPriority.MEDIUM


def test_facade_create_assign_update_cancel_workflow(db_session):
    from app.repositories.delivery_repository import DeliveryRepository
    from app.repositories.assignments import AssignmentRepository
    from app.repositories.notification_repository import NotificationRepository
    from app.repositories.driver_repository import DriverRepository
    from app.models import DeliveryStatus

    delivery_repository = DeliveryRepository(db_session)
    assignment_repository = AssignmentRepository(db_session)
    notification_repository = NotificationRepository(db_session)
    driver_repository = DriverRepository(db_session)
    facade = DeliveryManagementFacade(
        delivery_repository=delivery_repository,
        assignment_repository=assignment_repository,
        notification_repository=notification_repository,
        driver_repository=driver_repository,
    )

    delivery = facade.create_delivery(
        pickup="A",
        destination="B",
        deadline=datetime.utcnow(),
        priority=1,
        vehicle_id=1,
    )
    assert delivery.id is not None
    assert delivery.status == DeliveryStatus.PENDING

    assigned = facade.assign_delivery(delivery.id)
    assert assigned is not None
    assert assigned.status == DeliveryStatus.ASSIGNED

    summary = facade.get_delivery_summary(delivery.id)
    assert summary["delivery_id"] == delivery.id

    updated = facade.update_delivery_status(delivery.id, DeliveryStatus.COMPLETED)
    assert updated.status == DeliveryStatus.COMPLETED

    canceled = facade.cancel_delivery(delivery.id)
    assert canceled.status == DeliveryStatus.CANCELLED

    notifications = notification_repository.list()
    assert any(str(delivery.id) in note.message for note in notifications)
