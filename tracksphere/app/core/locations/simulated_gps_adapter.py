from __future__ import annotations
from datetime import datetime, timezone
import random
from typing import Optional
from sqlalchemy.orm import Session

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
    Simulates a hardware GPS provider.
    Translates fake hardware payloads into internal TrackSphereLocation domain models.
    """

    def __init__(self, db: Optional[Session] = None):
        self._seed = {}
        self.db = db
        
        if self.db:
            from app.repositories.vehicle_repository import VehicleRepository
            from app.repositories.location_repository import LocationRepository
            
            vehicles = VehicleRepository(self.db).list()
            loc_repo = LocationRepository(self.db)
            
            for v in vehicles:
                last_loc = loc_repo.get_latest_by_vehicle(v.id)
                if last_loc:
                    self._seed[v.id] = (last_loc.latitude, last_loc.longitude)
                else:
                    # Fallback to Dhaka hub if vehicle has no history
                    self._seed[v.id] = (23.8103, 90.4125)

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
            # Fallback filler location (Dhaka)
            base = (23.8103, 90.4125)
            self._seed[vehicle_id] = base
        return base

    def _translate(self, data: ExternalLocationData) -> TrackSphereLocation:
        return TrackSphereLocation(
            vehicle_id=getattr(data, "vehicle_id", 0),
            latitude=data.lat,
            longitude=data.lon,
            timestamp=datetime.fromisoformat(data.timestamp),
        )

