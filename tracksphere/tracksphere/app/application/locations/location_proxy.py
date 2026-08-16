from __future__ import annotations

from .location_models import TrackSphereLocation
from .location_service import TrackSphereLocationService
from tracksphere.app.models import UserRole
from tracksphere.app.models import User


class LocationServiceProxy:
    def __init__(self, real_service: TrackSphereLocationService, user: User):
        self.real_service = real_service
        self.user = user

    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        if self.user.role == UserRole.ADMINISTRATOR:
            return self.real_service.get_vehicle_location(vehicle_id)

        if self.user.role == UserRole.DISPATCHER:
            return self.real_service.get_vehicle_location(vehicle_id)

        if self.user.role == UserRole.DRIVER:
            if self.user.driver and (
                self.user.driver.id == vehicle_id
                or any(delivery.vehicle_id == vehicle_id for delivery in self.user.driver.deliveries)
            ):
                return self.real_service.get_vehicle_location(vehicle_id)
            raise PermissionError("Driver is not authorized to access this vehicle location")

        raise PermissionError("User is not authorized to access vehicle locations")

    def get_all_vehicle_locations(self, vehicles: list) -> list[TrackSphereLocation]:
        if self.user.role in (UserRole.ADMINISTRATOR, UserRole.DISPATCHER):
            target_ids = [v.id if hasattr(v, "id") else v for v in vehicles]
            if hasattr(self.real_service, "get_all_vehicle_locations"):
                return self.real_service.get_all_vehicle_locations(target_ids)
            return [self.real_service.get_vehicle_location(vid) for vid in target_ids]

        if self.user.role == UserRole.DRIVER:
            if not self.user.driver:
                return []
            allowed_ids = {
                delivery.vehicle_id
                for delivery in self.user.driver.deliveries
                if delivery.vehicle_id is not None
            }
            allowed_ids.add(self.user.driver.id)

            target_ids = [
                v.id if hasattr(v, "id") else v
                for v in vehicles
                if (v.id if hasattr(v, "id") else v) in allowed_ids
            ]
            if hasattr(self.real_service, "get_all_vehicle_locations"):
                return self.real_service.get_all_vehicle_locations(target_ids)
            return [self.real_service.get_vehicle_location(vid) for vid in target_ids]

        raise PermissionError("User is not authorized to access vehicle locations")

