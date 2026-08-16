from datetime import datetime

import pytest

from app.application.assignments.assignment_service import AssignmentError, AssignmentService
from app.application.assignments.strategy import (
    CapacityBasedStrategy,
    LeastBusyDriverStrategy,
    NearestDriverStrategy,
)
from app.models import AvailabilityStatus, Delivery, DeliveryStatus, Driver, User, UserRole


class DummyAssignmentRepository:
    def __init__(self):
        self.created = None

    def create_assignment(self, delivery_id: int, driver_id: int, vehicle_id=None, status=None):
        self.created = {
            "delivery_id": delivery_id,
            "driver_id": driver_id,
            "vehicle_id": vehicle_id,
            "status": status,
        }
        return self.created


def _build_delivery():
    return Delivery(
        pickup="Warehouse A",
        destination="Customer X",
        deadline=datetime.utcnow(),
        priority=1,
        status=DeliveryStatus.PENDING,
    )


def _build_driver(driver_id: int, available: bool = True, assignment_count: int = 0):
    user = User(
        name=f"Driver {driver_id}",
        email=f"driver{driver_id}@example.com",
        password_hash="secret",
        role=UserRole.DRIVER,
        active=True,
    )
    driver = Driver(user_id=driver_id, license_number=f"LIC-{driver_id}", availability=AvailabilityStatus.AVAILABLE if available else AvailabilityStatus.UNAVAILABLE)
    driver.id = driver_id
    driver.user = user
    driver.assignments = [None] * assignment_count
    return driver


def test_nearest_driver_strategy_prefers_first_available_driver():
    delivery = _build_delivery()
    drivers = [
        _build_driver(2, available=False),
        _build_driver(1, available=True),
        _build_driver(3, available=True),
    ]

    strategy = NearestDriverStrategy()
    chosen = strategy.select_driver(delivery, drivers)

    assert chosen is not None
    assert chosen.id == 1


def test_least_busy_driver_strategy_selects_fewest_assignments():
    delivery = _build_delivery()
    drivers = [
        _build_driver(1, assignment_count=2),
        _build_driver(2, assignment_count=1),
        _build_driver(3, assignment_count=3),
    ]

    strategy = LeastBusyDriverStrategy()
    chosen = strategy.select_driver(delivery, drivers)

    assert chosen is not None
    assert chosen.id == 2


def test_capacity_based_strategy_skips_overloaded_drivers():
    delivery = _build_delivery()
    drivers = [
        _build_driver(1, assignment_count=3),
        _build_driver(2, assignment_count=2),
        _build_driver(3, assignment_count=4),
    ]

    strategy = CapacityBasedStrategy()
    chosen = strategy.select_driver(delivery, drivers)

    assert chosen is not None
    assert chosen.id == 2


def test_assignment_service_uses_strategy_and_repository():
    delivery = _build_delivery()
    driver = _build_driver(1, assignment_count=1)
    repository = DummyAssignmentRepository()
    service = AssignmentService(LeastBusyDriverStrategy(), repository)

    assignment = service.assign(delivery, [driver])

    assert assignment["delivery_id"] == delivery.id
    assert assignment["driver_id"] == driver.id
    assert repository.created["driver_id"] == driver.id


def test_assignment_service_raises_when_no_driver_available():
    delivery = _build_delivery()
    driver = _build_driver(1, available=False)
    repository = DummyAssignmentRepository()
    service = AssignmentService(NearestDriverStrategy(), repository)

    with pytest.raises(AssignmentError):
        service.assign(delivery, [driver])
