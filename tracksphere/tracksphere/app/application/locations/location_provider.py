from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol

from .location_models import TrackSphereLocation


class LocationProvider(ABC):
    @abstractmethod
    def fetch_location(self, vehicle_id: int) -> TrackSphereLocation:
        raise NotImplementedError


class ExternalLocationData(Protocol):
    lat: float
    lon: float
    timestamp: str
