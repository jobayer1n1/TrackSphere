from typing import Protocol

from .location_models import TrackSphereLocation
from .location_provider import LocationProvider


class LocationService(Protocol):
    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        ...

    def get_all_vehicle_locations(self, vehicle_ids: list[int]) -> list[TrackSphereLocation]:
        ...


class TrackSphereLocationService:
    def __init__(self, provider: LocationProvider):
        self.provider = provider

    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        return self.provider.fetch_location(vehicle_id)

    def get_all_vehicle_locations(self, vehicle_ids: list[int]) -> list[TrackSphereLocation]:
        return [self.provider.fetch_location(vid) for vid in vehicle_ids]

