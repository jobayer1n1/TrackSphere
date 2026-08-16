from datetime import datetime

from app.application.assignments import AssignmentService
from app.application.assignments.strategy import LeastBusyDriverStrategy
from app.application.notifications import (
    DashboardObserver,
    DeliveryAssignedEvent,
    DeliveryEventSource,
    NotificationObserver,
)
from app.models import (
    AssignmentStatus,
    Delivery,
    DeliveryPriority,
    DeliveryStatus,
    Driver,
    Notification,
    NotificationPriority,
    NotificationType,
    User,
    UserRole,
)
from app.repositories import AssignmentRepository, NotificationRepository


def test_delivery_assignment_creates_notification_and_updates_dashboard(db_session):
    user = User(name="Dispatcher", email="dispatcher@example.com", password_hash="pw", role=UserRole.DISPATCHER, active=True)
    driver_user = User(name="Driver One", email="driver1@example.com", password_hash="pw", role=UserRole.DRIVER, active=True)
    db_session.add_all([user, driver_user])
    db_session.flush()

    driver = Driver(user_id=driver_user.id, license_number="LIC-201", availability="AVAILABLE")
    db_session.add(driver)
    db_session.flush()

    delivery = Delivery(
        pickup="Warehouse A",
        destination="Customer B",
        deadline=datetime.utcnow(),
        priority=DeliveryPriority.MEDIUM,
        status=DeliveryStatus.PENDING,
    )
    db_session.add(delivery)
    db_session.flush()

    assignment_repo = AssignmentRepository(db_session)
    notification_repo = NotificationRepository(db_session)

    subject = DeliveryEventSource()
    dashboard = DashboardObserver()
    notification_observer = NotificationObserver(notification_repo, user)
    subject.attach(dashboard)
    subject.attach(notification_observer)

    service = AssignmentService(LeastBusyDriverStrategy(), assignment_repo)
    assignment = service.assign(delivery, [driver])

    before_count = len(notification_repo.list())
    event = DeliveryAssignedEvent(
        delivery_id=delivery.id,
        timestamp=datetime.utcnow(),
        event_type="assigned",
        details="Delivery assigned",
        driver_id=driver.id,
        vehicle_id=None,
    )
    subject.notify(event)

    notifications = notification_repo.list()
    assert len(notifications) == before_count + 1
    assert any(
        notification.message == f"Delivery {delivery.id} assigned to driver {driver.id}."
        for notification in notifications
    )
    assert dashboard.latest_event() == event
    assert assignment.delivery_id == delivery.id
    assert assignment.driver_id == driver.id
    assert assignment.status == AssignmentStatus.PENDING
