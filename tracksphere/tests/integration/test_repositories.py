from sqlalchemy import select

from datetime import datetime

from app.models import User, Driver, Vehicle, Delivery, Notification, Location, UserRole, AvailabilityStatus, VehicleStatus, DeliveryStatus, NotificationType, NotificationPriority
from app.repositories.user_repository import UserRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.location_repository import LocationRepository


def test_user_repository_crud(db_session):
    user_repo = UserRepository(db_session)
    user = User(name="Repo User", email="repo@example.com", password_hash="pass", role=UserRole.DISPATCHER, active=True)
    user_repo.create(user)
    assert user.id is not None

    fetched = user_repo.get(user.id)
    assert fetched.email == "repo@example.com"

    user_repo.update(fetched, name="Repo Updated")
    assert fetched.name == "Repo Updated"

    user_repo.delete(fetched)
    assert user_repo.get(user.id) is None


def test_driver_repository_relationship(db_session):
    user = User(name="Driver Repo", email="driver_repo@example.com", password_hash="pass", role=UserRole.DRIVER, active=True)
    db_session.add(user)
    db_session.flush()

    driver_repo = DriverRepository(db_session)
    driver = Driver(user_id=user.id, license_number="LIC-101", availability=AvailabilityStatus.AVAILABLE)
    driver_repo.create(driver)

    assert driver.user.id == user.id
    assert driver_repo.get(driver.id).user.email == "driver_repo@example.com"


def test_vehicle_repository_crud(db_session):
    vehicle_repo = VehicleRepository(db_session)
    vehicle = Vehicle(registration_number="REG-101", vehicle_type="Car", capacity=500, status=VehicleStatus.AVAILABLE)
    vehicle_repo.create(vehicle)
    fetched = vehicle_repo.get(vehicle.id)
    assert fetched.registration_number == "REG-101"
    vehicle_repo.update(fetched, status=VehicleStatus.MAINTENANCE)
    assert fetched.status == VehicleStatus.MAINTENANCE
    vehicle_repo.delete(fetched)
    assert vehicle_repo.get(vehicle.id) is None


def test_delivery_repository_relationships(db_session):
    user = User(name="Delivery Driver", email="delivery_driver@example.com", password_hash="pass", role=UserRole.DRIVER, active=True)
    db_session.add(user)
    db_session.flush()
    driver = Driver(user_id=user.id, license_number="LIC-102", availability=AvailabilityStatus.AVAILABLE)
    db_session.add(driver)
    vehicle = Vehicle(registration_number="REG-102", vehicle_type="Van", capacity=1000, status=VehicleStatus.AVAILABLE)
    db_session.add(vehicle)
    db_session.flush()

    delivery_repo = DeliveryRepository(db_session)
    delivery = Delivery(
        pickup="A",
        destination="B",
        deadline=datetime(2026, 12, 31, 23, 59, 59),
        priority=1,
        status=DeliveryStatus.PENDING,
        driver_id=driver.id,
        vehicle_id=vehicle.id,
    )
    delivery_repo.create(delivery)

    assert delivery_repo.get(delivery.id).driver.id == driver.id
    assert delivery_repo.get(delivery.id).vehicle.id == vehicle.id


def test_notification_repository_relationship(db_session):
    user = User(name="Notify User", email="notify@example.com", password_hash="pass", role=UserRole.DISPATCHER, active=True)
    db_session.add(user)
    db_session.flush()

    notification_repo = NotificationRepository(db_session)
    notification = Notification(
        recipient_id=user.id,
        message="Test",
        notification_type=NotificationType.INFO,
        priority=NotificationPriority.LOW,
        read=False,
    )
    notification_repo.create(notification)

    assert notification_repo.get(notification.id).recipient.id == user.id


def test_location_repository_relationship(db_session):
    vehicle = Vehicle(registration_number="REG-103", vehicle_type="Truck", capacity=1500, status=VehicleStatus.AVAILABLE)
    db_session.add(vehicle)
    db_session.flush()

    location_repo = LocationRepository(db_session)
    location = Location(vehicle_id=vehicle.id, latitude=12.34, longitude=56.78)
    location_repo.create(location)
    assert location_repo.get(location.id).vehicle.id == vehicle.id
