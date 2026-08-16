from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.application.auth import hash_password
from tracksphere.app.models import (
    AssignmentStatus,
    Delivery,
    DeliveryPriority,
    DeliveryStatus,
    Driver,
    Location,
    Notification,
    NotificationPriority,
    NotificationType,
    User,
    UserRole,
    Vehicle,
    VehicleStatus,
)


def _exists(session: Session, model, **kwargs) -> bool:
    return session.execute(select(model).filter_by(**kwargs)).scalars().first() is not None


def seed_data(session: Session) -> None:
    if _exists(session, User, email="admin@tracksphere.local"):
        return

    admin = User(
        name="Admin User",
        email="admin@tracksphere.local",
        password_hash=hash_password("adminpass"),
        role=UserRole.ADMINISTRATOR,
        active=True,
    )
    dispatcher = User(
        name="Dispatch Lead",
        email="dispatcher@tracksphere.local",
        password_hash=hash_password("dispatchpass"),
        role=UserRole.DISPATCHER,
        active=True,
    )
    driver_user_1 = User(
        name="Driver One",
        email="driver1@tracksphere.local",
        password_hash=hash_password("driver1pass"),
        role=UserRole.DRIVER,
        active=True,
    )
    driver_user_2 = User(
        name="Driver Two",
        email="driver2@tracksphere.local",
        password_hash=hash_password("driver2pass"),
        role=UserRole.DRIVER,
        active=True,
    )

    session.add_all([admin, dispatcher, driver_user_1, driver_user_2])
    session.flush()

    driver_1 = Driver(
        user_id=driver_user_1.id,
        license_number="DRV-1001",
        availability="AVAILABLE",
    )
    driver_2 = Driver(
        user_id=driver_user_2.id,
        license_number="DRV-1002",
        availability="AVAILABLE",
    )

    vehicle_1 = Vehicle(
        registration_number="REG-01",
        vehicle_type="Van",
        capacity=1200,
        status=VehicleStatus.AVAILABLE,
    )
    vehicle_2 = Vehicle(
        registration_number="REG-02",
        vehicle_type="Truck",
        capacity=2400,
        status=VehicleStatus.AVAILABLE,
    )

    session.add_all([driver_1, driver_2, vehicle_1, vehicle_2])
    session.flush()

    now = datetime.utcnow()
    delivery_1 = Delivery(
        pickup="Warehouse A",
        destination="Customer X",
        deadline=now + timedelta(hours=4),
        priority=1,
        status=DeliveryStatus.PENDING,
        notes="Fragile package",
    )
    delivery_2 = Delivery(
        pickup="Warehouse B",
        destination="Customer Y",
        deadline=now + timedelta(hours=6),
        priority=2,
        status=DeliveryStatus.PENDING,
        notes="Requires appointment",
    )
    delivery_3 = Delivery(
        pickup="Hub C",
        destination="Customer Z",
        deadline=now + timedelta(hours=3),
        priority=1,
        status=DeliveryStatus.ASSIGNED,
        driver_id=driver_1.id,
        vehicle_id=vehicle_1.id,
        notes="High-value shipment",
    )

    session.add_all([delivery_1, delivery_2, delivery_3])
    session.flush()

    notification_1 = Notification(
        recipient_id=dispatcher.id,
        message="New delivery request created.",
        notification_type=NotificationType.INFO,
        priority=NotificationPriority.MEDIUM,
        read=False,
    )
    notification_2 = Notification(
        recipient_id=driver_user_1.id,
        message="You have been assigned a delivery.",
        notification_type=NotificationType.ALERT,
        priority=NotificationPriority.HIGH,
        read=False,
    )

    location_1 = Location(
        vehicle_id=vehicle_1.id,
        latitude=40.7128,
        longitude=-74.0060,
    )
    location_2 = Location(
        vehicle_id=vehicle_2.id,
        latitude=34.0522,
        longitude=-118.2437,
    )

    session.add_all([notification_1, notification_2, location_1, location_2])
    session.commit()
