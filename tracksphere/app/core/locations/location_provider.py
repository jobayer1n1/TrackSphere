from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol

from app.core.locations.location_models import TrackSphereLocation


class LocationProvider(ABC):
    """
    Target Interface for Location telemetry providers (Adapter Pattern).
    """

    @abstractmethod
    def fetch_location(self, vehicle_id: int) -> TrackSphereLocation:
        """Fetch current location for a given vehicle."""
        raise NotImplementedError


class ExternalLocationData(Protocol):
    """
    Protocol for external unstructured GPS feeds.
    """
    lat: float
    lon: float
    timestamp: str
