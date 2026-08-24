from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session

from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_service import LocationService
from app.models.driver import Driver
from app.models.enums import DeliveryStatus
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.driver_repository import DriverRepository


class DriverNotAssignedError(Exception):
    """Raised when querying the location of a driver who is not assigned to any vehicle."""
    pass


class DriverLocationProvider(ABC):
    """
    Target Interface for Driver Location telemetry (Adapter Pattern).
    Defines contract for retrieving driver location telemetry.
    """

    @abstractmethod
    def get_driver_location(self, driver_id: int) -> TrackSphereLocation:
        """
        Fetch current live location for a given driver.
        Raises DriverNotAssignedError if driver is not assigned to any vehicle.
        """
        raise NotImplementedError


class DriverLocationAdapter(DriverLocationProvider):
    """
    Adapter Pattern:
    Adapts Driver location requests to the underlying LocationService (which operates on vehicle_id).
    
    Since physical GPS telemetry belongs to vehicles (the adaptee), this adapter:
    1. Looks up the driver's active vehicle assignment.
    2. If assigned, delegates to the LocationService to fetch that vehicle's live coordinates.
    3. If unassigned, raises DriverNotAssignedError ("Driver is not assigned to any vehicle").
    """

    def __init__(self, location_service: LocationService, db: Session):
        self.location_service = location_service
        self.db = db

    def get_assigned_vehicle_id(self, driver_id: int) -> Optional[int]:
        """
        Determine the vehicle_id actively assigned to the given driver.
        Checks active deliveries (IN_PROGRESS or ASSIGNED).
        """
        driver = DriverRepository(self.db).get(driver_id)
        if not driver:
            return None

        # Check active deliveries for this driver
        delivery_repo = DeliveryRepository(self.db)
        driver_deliveries = delivery_repo.list_by_driver(driver_id)
        for d in driver_deliveries:
            if d.status in [DeliveryStatus.IN_PROGRESS, DeliveryStatus.ASSIGNED] and d.vehicle_id:
                return d.vehicle_id

        # Check assignments with active delivery status
        if hasattr(driver, "assignments") and driver.assignments:
            for a in driver.assignments:
                if a.vehicle_id and getattr(a, "delivery", None):
                    if a.delivery.status in [DeliveryStatus.IN_PROGRESS, DeliveryStatus.ASSIGNED]:
                        return a.vehicle_id

        return None

    def get_driver_location(self, driver_id: int) -> TrackSphereLocation:
        """
        Adapter method: translates driver_id -> vehicle_id -> LocationService.get_vehicle_location(vehicle_id)
        """
        driver = DriverRepository(self.db).get(driver_id)
        if not driver:
            raise DriverNotAssignedError(f"Driver #{driver_id} not found.")

        vehicle_id = self.get_assigned_vehicle_id(driver_id)
        if not vehicle_id:
            raise DriverNotAssignedError("Driver is not assigned to any vehicle.")

        # Delegate to underlying vehicle location service (Adaptee)
        return self.location_service.get_vehicle_location(vehicle_id)
