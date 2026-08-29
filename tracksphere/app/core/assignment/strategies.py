from abc import ABC, abstractmethod
from app.models.driver import Driver
from app.models.enums import AvailabilityStatus, VehicleStatus
from app.models.vehicle import Vehicle


class AssignmentStrategy(ABC):
    """
    Strategy Pattern Interface:
    Defines algorithm interface for determining if a Driver and Vehicle are eligible for job assignment.
    """

    @abstractmethod
    def is_eligible(self, driver: Driver, vehicle: Vehicle) -> tuple[bool, str]:
        """
        Evaluate driver and vehicle eligibility.
        Returns (is_eligible, reason_if_not).
        """
        raise NotImplementedError


class DefaultAvailabilityStrategy(AssignmentStrategy):
    """
    Default Strategy:
    Checks if driver is AVAILABLE and vehicle is AVAILABLE (not in maintenance or already assigned).
    """

    def is_eligible(self, driver: Driver, vehicle: Vehicle) -> tuple[bool, str]:
        if not driver:
            return False, "Driver not found."

        if driver.availability != AvailabilityStatus.AVAILABLE:
            return False, f"Driver {driver.license_number} is currently marked {driver.availability.value}."

        if not vehicle:
            return False, "Vehicle not found."

        if vehicle.status == VehicleStatus.MAINTENANCE:
            return False, f"Vehicle {vehicle.registration_number} is currently in MAINTENANCE."

        if vehicle.status == VehicleStatus.ASSIGNED:
            return False, f"Vehicle {vehicle.registration_number} is already ASSIGNED to another active job."

        return True, "Driver and Vehicle are eligible for assignment."


class HighPriorityStrategy(AssignmentStrategy):
    """
    High Priority Strategy:
    Requires minimum vehicle capacity and active driver license verification.
    """

    def is_eligible(self, driver: Driver, vehicle: Vehicle) -> tuple[bool, str]:
        base_eligible, reason = DefaultAvailabilityStrategy().is_eligible(driver, vehicle)
        if not base_eligible:
            return False, reason

        if vehicle.capacity < 2000:
            return False, f"High priority delivery requires vehicle capacity >= 2000kg (Vehicle {vehicle.registration_number} has {vehicle.capacity}kg)."

        return True, "Eligible for high-priority assignment."


def get_assignment_strategy(
    strategy_name: str | None = None, priority: int | None = None
) -> AssignmentStrategy:
    """
    Strategy Resolver / Factory helper:
    Dynamically select the appropriate AssignmentStrategy based on explicit strategy name
    or delivery priority level (e.g. priority >= 3 -> HighPriorityStrategy).
    """
    if strategy_name:
        name_clean = strategy_name.lower().replace("-", "_").replace(" ", "_")
        if name_clean in ("high_priority", "highpriority", "high"):
            return HighPriorityStrategy()
        if name_clean in ("default", "default_availability", "standard"):
            return DefaultAvailabilityStrategy()

    # Automatically select based on job priority if priority >= 3 (High)
    if priority is not None and priority >= 3:
        return HighPriorityStrategy()

    return DefaultAvailabilityStrategy()

