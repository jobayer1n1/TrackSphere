from __future__ import annotations
from datetime import datetime
import math
import time

from .location_models import TrackSphereLocation
from .location_provider import ExternalLocationData, LocationProvider


class SimulatedGPSData:
    def __init__(self, vehicle_id: int, lat: float, lon: float, timestamp: str):
        self.vehicle_id = vehicle_id
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp


class SimulatedGPSAdapter(LocationProvider):
    _seed = {
        1: (40.7128, -74.0060),
        2: (34.0522, -118.2437),
        3: (41.8781, -87.6298),
    }

    def __init__(self):
        pass


    def fetch_location(self, vehicle_id: int) -> TrackSphereLocation:
        lat, lon = self._get_coordinates(vehicle_id)
        external = SimulatedGPSData(
            vehicle_id=vehicle_id,
            lat=lat,
            lon=lon,
            timestamp=datetime.utcnow().isoformat(),
        )
        return self._translate(external)

    def _get_coordinates(self, vehicle_id: int) -> tuple[float, float]:
        return self._seed.get(vehicle_id, (37.7749, -122.4194))


    def _translate(self, data: ExternalLocationData) -> TrackSphereLocation:
        return TrackSphereLocation(
            vehicle_id=data.vehicle_id,
            latitude=data.lat,
            longitude=data.lon,
            timestamp=datetime.fromisoformat(data.timestamp),
        )

