from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session

from app.core.locations.location_models import TrackSphereLocation
from app.models.location import Location
from app.repositories.location_repository import LocationRepository


class Observer(ABC):
    """
    Observer Pattern: Target interface for components listening to real-time telemetry or domain events.
    """

    @abstractmethod
    def update(self, event_type: str, data: dict[str, Any]) -> None:
        """Receive notification update from Subject."""
        raise NotImplementedError


class GPSTrackingSubject:
    """
    Observer Pattern Subject:
    Maintains registered listeners and broadcasts GPS location updates or transit alerts.
    """

    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event_type: str, data: dict[str, Any]) -> None:
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                # Prevent failure in one observer from blocking others
                print(f"[GPSTrackingSubject] Observer update failed: {e}")

    def receive_location_update(
        self, db: Session, location: TrackSphereLocation
    ) -> Location:
        """
        Record location update in the database and notify all registered observers.
        """
        location_repo = LocationRepository(db)
        db_location = Location(
            vehicle_id=location.vehicle_id,
            latitude=location.latitude,
            longitude=location.longitude,
            timestamp=location.timestamp or datetime.now(timezone.utc),
        )
        saved_loc = location_repo.create(db_location)

        payload = {
            "vehicle_id": location.vehicle_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "timestamp": location.timestamp.isoformat(),
        }
        self.notify_observers("LOCATION_UPDATE", payload)
        return saved_loc


# Global singleton instance of GPSTrackingSubject
tracking_subject = GPSTrackingSubject()
