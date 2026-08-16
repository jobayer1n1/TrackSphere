from abc import ABC, abstractmethod
from typing import List, Optional

from tracksphere.app.models import AvailabilityStatus, Delivery, Driver


class AssignmentStrategy(ABC):
    """Defines the interface for delivery assignment strategies."""

    @abstractmethod
    def select_driver(self, delivery: Delivery, drivers: List[Driver]) -> Optional[Driver]:
        raise NotImplementedError


class NearestDriverStrategy(AssignmentStrategy):
    """Selects the most readily available driver by simple proximity heuristic."""

    def select_driver(self, delivery: Delivery, drivers: List[Driver]) -> Optional[Driver]:
        available_drivers = [driver for driver in drivers if driver.availability == AvailabilityStatus.AVAILABLE]
        if not available_drivers:
            return None

        # In this simplified implementation, the nearest available driver is chosen by a deterministic
        # ordering on the driver ID to illustrate a strategy switch without directly modeling geography.
        return min(available_drivers, key=lambda driver: driver.id)


class LeastBusyDriverStrategy(AssignmentStrategy):
    """Selects the available driver with the fewest active assignments."""

    def select_driver(self, delivery: Delivery, drivers: List[Driver]) -> Optional[Driver]:
        available_drivers = [driver for driver in drivers if driver.availability == AvailabilityStatus.AVAILABLE]
        if not available_drivers:
            return None
        return min(available_drivers, key=lambda driver: len(driver.assignments or []))


class CapacityBasedStrategy(AssignmentStrategy):
    """Selects a driver who is available and not yet overloaded."""

    def select_driver(self, delivery: Delivery, drivers: List[Driver]) -> Optional[Driver]:
        available_drivers = [
            driver
            for driver in drivers
            if driver.availability == AvailabilityStatus.AVAILABLE and len(driver.assignments or []) < 3
        ]
        if not available_drivers:
            return None
        return min(available_drivers, key=lambda driver: len(driver.assignments or []))
