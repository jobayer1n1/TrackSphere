from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session

from app.core.locations.driver_location_adapter import DriverLocationAdapter, DriverNotAssignedError
from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_service import TrackSphereLocationService
from app.models.enums import UserRole
from app.models.user import User


class LocationServiceProxy:
    """
    Protection Proxy Pattern:
    Controls access to the real TrackSphereLocationService based on the requesting User's role and assignments.
    - Administrator & Dispatcher: Full unrestricted telemetry access across all fleet vehicles and drivers.
    - Driver: Restricted strictly to the vehicle actively assigned to their deliveries and their own profile.
    - Unauthorized: Raises PermissionError.
    """

    def __init__(
        self,
        real_service: TrackSphereLocationService,
        user: User | Any,
        db: Session | None = None,
    ):
        self.real_service = real_service
        self.user = user
        self.db = db

    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        if not self.user:
            raise PermissionError("Authentication required to access vehicle locations")

        user_role = getattr(self.user, "role", None)

        if user_role in (UserRole.ADMINISTRATOR, UserRole.DISPATCHER):
            return self.real_service.get_vehicle_location(vehicle_id)

        if user_role == UserRole.DRIVER:
            driver = getattr(self.user, "driver", None)
            if driver:
                # Check active deliveries
                driver_deliveries = getattr(driver, "deliveries", [])
                is_assigned = any(getattr(d, "vehicle_id", None) == vehicle_id for d in driver_deliveries)
                
                # Check assignments table
                driver_assignments = getattr(driver, "assignments", [])
                is_in_assignments = any(getattr(a, "vehicle_id", None) == vehicle_id for a in driver_assignments)

                if is_assigned or is_in_assignments:
                    return self.real_service.get_vehicle_location(vehicle_id)

            raise PermissionError("Driver is not authorized to access this vehicle location")

        raise PermissionError("User is not authorized to access vehicle locations")

    def get_driver_location(self, driver_id: int | None = None) -> TrackSphereLocation:
        """
        Retrieve driver telemetry via DriverLocationAdapter (Adapter Pattern) with RBAC protection.
        Raises DriverNotAssignedError if driver is not assigned to any vehicle.
        """
        if not self.user:
            raise PermissionError("Authentication required to access driver location")

        if not self.db:
            raise ValueError("Database session is required to resolve driver assignment.")

        user_role = getattr(self.user, "role", None)
        target_driver_id: int | None = driver_id

        if user_role == UserRole.DRIVER:
            driver = getattr(self.user, "driver", None)
            if not driver:
                raise PermissionError("Driver profile not found")
            if target_driver_id is not None and target_driver_id != driver.id:
                raise PermissionError("Driver is not authorized to access another driver's location")
            target_driver_id = driver.id

        if target_driver_id is None:
            raise ValueError("Driver ID must be specified.")

        adapter = DriverLocationAdapter(self.real_service, self.db)
        return adapter.get_driver_location(target_driver_id)


