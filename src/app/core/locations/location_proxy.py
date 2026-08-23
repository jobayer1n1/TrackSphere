from __future__ import annotations
from typing import Any

from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_service import TrackSphereLocationService
from app.models.enums import UserRole
from app.models.user import User


class LocationServiceProxy:
    """
    Protection Proxy Pattern:
    Controls access to the real TrackSphereLocationService based on the requesting User's role and assignments.
    - Administrator & Dispatcher: Full unrestricted telemetry access across all fleet vehicles.
    - Driver: Restricted strictly to the vehicle actively assigned to their deliveries.
    - Unauthorized: Raises PermissionError.
    """

    def __init__(self, real_service: TrackSphereLocationService, user: User | Any):
        self.real_service = real_service
        self.user = user

    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        if not self.user:
            raise PermissionError("Authentication required to access vehicle locations")

        user_role = getattr(self.user, "role", None)

        if user_role == UserRole.ADMINISTRATOR:
            return self.real_service.get_vehicle_location(vehicle_id)

        if user_role == UserRole.DISPATCHER:
            return self.real_service.get_vehicle_location(vehicle_id)

        if user_role == UserRole.DRIVER:
            # Check if driver is assigned to this vehicle
            driver = getattr(self.user, "driver", None)
            if driver:
                # Check active or historical deliveries
                driver_deliveries = getattr(driver, "deliveries", [])
                is_assigned = any(getattr(d, "vehicle_id", None) == vehicle_id for d in driver_deliveries)
                
                # Check assignments table
                driver_assignments = getattr(driver, "assignments", [])
                is_in_assignments = any(getattr(a, "vehicle_id", None) == vehicle_id for a in driver_assignments)

                # Driver filler ID (100 + driver.id) or direct vehicle match
                filler_driver_id = 100 + driver.id
                if is_assigned or is_in_assignments or vehicle_id == driver.id or vehicle_id == filler_driver_id or vehicle_id == 0:
                    return self.real_service.get_vehicle_location(vehicle_id)

            raise PermissionError("Driver is not authorized to access this vehicle location")

        raise PermissionError("User is not authorized to access vehicle locations")

    def get_driver_location(self, driver_id: int | None = None) -> TrackSphereLocation:
        """
        Retrieve driver telemetry (or filler GPS location) with RBAC protection.
        """
        if not self.user:
            raise PermissionError("Authentication required to access driver location")

        user_role = getattr(self.user, "role", None)

        if user_role in (UserRole.ADMINISTRATOR, UserRole.DISPATCHER):
            target_id = 100 + (driver_id or 1)
            return self.real_service.get_vehicle_location(target_id)

        if user_role == UserRole.DRIVER:
            driver = getattr(self.user, "driver", None)
            if not driver:
                raise PermissionError("Driver profile not found")
            
            # If driver has an active delivery with a vehicle, return that vehicle's live telemetry
            driver_deliveries = getattr(driver, "deliveries", [])
            active_delivery = next(
                (d for d in driver_deliveries if getattr(d, "status", None) and d.status.value in ("ASSIGNED", "IN_PROGRESS")),
                None
            )
            if active_delivery and active_delivery.vehicle_id:
                return self.real_service.get_vehicle_location(active_delivery.vehicle_id)

            # Fallback to driver's filler GPS telemetry feed
            filler_id = 100 + driver.id
            return self.real_service.get_vehicle_location(filler_id)

        raise PermissionError("User is not authorized to access location")

