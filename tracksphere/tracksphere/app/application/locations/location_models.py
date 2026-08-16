from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrackSphereLocation:
    vehicle_id: int
    latitude: float
    longitude: float
    timestamp: datetime
