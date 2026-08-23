from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.assignment.strategies import AssignmentStrategy, DefaultAvailabilityStrategy
from app.models.assignment import Assignment
from app.models.enums import AssignmentStatus, AvailabilityStatus, DeliveryStatus, VehicleStatus
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.vehicle_repository import VehicleRepository


class AssignmentService:
    """
    Core Domain Service managing delivery assignments.
    Uses AssignmentStrategy (Strategy Pattern) to dynamically validate eligibility.
    """

    def __init__(self, strategy: AssignmentStrategy | None = None):
        self.strategy: AssignmentStrategy = strategy or DefaultAvailabilityStrategy()

    def set_strategy(self, strategy: AssignmentStrategy) -> None:
        """Switch strategy dynamically at runtime."""
        self.strategy = strategy

    def assign_delivery(
        self, db: Session, delivery_id: int, driver_id: int, vehicle_id: int
    ) -> tuple[Assignment | None, str]:
        delivery_repo = DeliveryRepository(db)
        driver_repo = DriverRepository(db)
        vehicle_repo = VehicleRepository(db)
        assignment_repo = AssignmentRepository(db)

        delivery = delivery_repo.get(delivery_id)
        if not delivery:
            return None, "Delivery job not found."

        if delivery.status in [DeliveryStatus.COMPLETED, DeliveryStatus.CANCELLED]:
            return None, f"Cannot assign delivery in {delivery.status.value} status."

        driver = driver_repo.get(driver_id)
        if not driver:
            return None, "Driver not found."

        vehicle = vehicle_repo.get(vehicle_id)
        if not vehicle:
            return None, "Vehicle not found."

        # Validate eligibility using Strategy Pattern
        is_eligible, reason = self.strategy.is_eligible(driver, vehicle)
        if not is_eligible:
            return None, reason

        # Create Assignment record
        assignment = Assignment(
            delivery_id=delivery.id,
            driver_id=driver.id,
            vehicle_id=vehicle.id,
            assigned_at=datetime.now(timezone.utc),
            status=AssignmentStatus.CONFIRMED,
        )
        created_assignment = assignment_repo.create(assignment)

        # Update Delivery status and references
        delivery_repo.update(
            delivery,
            status=DeliveryStatus.ASSIGNED,
            driver_id=driver.id,
            vehicle_id=vehicle.id,
        )

        # Update Driver availability
        driver_repo.update(driver, availability=AvailabilityStatus.UNAVAILABLE)

        # Update Vehicle status
        vehicle_repo.update(vehicle, status=VehicleStatus.ASSIGNED)

        return created_assignment, "Assignment successfully confirmed."

    def unassign_delivery(self, db: Session, delivery_id: int) -> tuple[bool, str]:
        delivery_repo = DeliveryRepository(db)
        driver_repo = DriverRepository(db)
        vehicle_repo = VehicleRepository(db)
        assignment_repo = AssignmentRepository(db)

        delivery = delivery_repo.get(delivery_id)
        if not delivery:
            return False, "Delivery not found."

        if delivery.driver_id:
            driver = driver_repo.get(delivery.driver_id)
            if driver:
                driver_repo.update(driver, availability=AvailabilityStatus.AVAILABLE)

        if delivery.vehicle_id:
            vehicle = vehicle_repo.get(delivery.vehicle_id)
            if vehicle:
                vehicle_repo.update(vehicle, status=VehicleStatus.AVAILABLE)

        # Mark assignment as cancelled
        assignment = assignment_repo.get_by_delivery(delivery.id)
        if assignment:
            assignment_repo.update(assignment, status=AssignmentStatus.CANCELLED)

        delivery_repo.update(
            delivery,
            status=DeliveryStatus.PENDING,
            driver_id=None,
            vehicle_id=None,
        )

        return True, "Delivery assignment cleared."
