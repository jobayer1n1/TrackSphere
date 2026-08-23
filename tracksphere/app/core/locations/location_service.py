from typing import Protocol

from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_provider import LocationProvider


class LocationService(Protocol):
    """
    Protocol defining the location retrieval contract.
    """
    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        ...


class TrackSphereLocationService:
    """
    Concrete Real Subject implementation of LocationService.
    """
    def __init__(self, provider: LocationProvider):
        self.provider = provider

    def get_vehicle_location(self, vehicle_id: int) -> TrackSphereLocation:
        return self.provider.fetch_location(vehicle_id)
