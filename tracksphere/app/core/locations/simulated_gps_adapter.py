from __future__ import annotations
from datetime import datetime, timezone
import random

from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_provider import ExternalLocationData, LocationProvider


class SimulatedGPSData:
    """
    Adaptee representation: External GPS device payload.
    """
    def __init__(self, vehicle_id: int, lat: float, lon: float, timestamp: str):
        self.vehicle_id = vehicle_id
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp


class SimulatedGPSAdapter(LocationProvider):
    """
    Adapter Pattern:
    Adapts simulated coordinate feeds (and hardware feeds) to the standard TrackSphereLocation domain structure.
    """

    # Shared coordinate registry for vehicle telemetry feeds
    _shared_seed: dict[int, tuple[float, float]] = {
        1: (40.7128, -74.0060),  # Vehicle 1: New York hub
        2: (34.0522, -118.2437), # Vehicle 2: Los Angeles hub (assigned to Sarah Connor)
        3: (41.8781, -87.6298),  # Vehicle 3: Chicago hub
        4: (29.7604, -95.3698),  # Vehicle 4: Houston hub
    }

    def __init__(self):
        self._seed = SimulatedGPSAdapter._shared_seed

    def fetch_location(self, vehicle_id: int) -> TrackSphereLocation:
        lat, lon = self._get_coordinates(vehicle_id)
        external = SimulatedGPSData(
            vehicle_id=vehicle_id,
            lat=lat,
            lon=lon,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        return self._translate(external)

    def set_coordinates(self, vehicle_id: int, lat: float, lon: float) -> None:
        """Update seed coordinate for a vehicle or driver."""
        self._seed[vehicle_id] = (lat, lon)

    def _get_coordinates(self, vehicle_id: int) -> tuple[float, float]:
        base = self._seed.get(vehicle_id)
        if not base:
            # Fallback filler location for any unspecified driver/vehicle (NYC Central Logistics Hub)
            base = (40.7580, -73.9855)
            self._seed[vehicle_id] = base

        return base

    def _translate(self, data: ExternalLocationData) -> TrackSphereLocation:
        return TrackSphereLocation(
            vehicle_id=getattr(data, "vehicle_id", 0),
            latitude=data.lat,
            longitude=data.lon,
            timestamp=datetime.fromisoformat(data.timestamp),
        )

