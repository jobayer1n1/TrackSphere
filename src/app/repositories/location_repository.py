from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location
from app.repositories.base import RepositoryBase


class LocationRepository(RepositoryBase[Location]):
    def list(self) -> List[Location]:
        return list(self.session.scalars(select(Location).order_by(Location.timestamp.desc())).all())

    def get(self, location_id: int) -> Optional[Location]:
        return self.session.get(Location, location_id)

    def get_latest_by_vehicle(self, vehicle_id: int) -> Optional[Location]:
        return self.session.scalars(
            select(Location)
            .where(Location.vehicle_id == vehicle_id)
            .order_by(Location.timestamp.desc())
        ).first()

    def get_history_by_vehicle(self, vehicle_id: int, limit: int = 50) -> List[Location]:
        return list(
            self.session.scalars(
                select(Location)
                .where(Location.vehicle_id == vehicle_id)
                .order_by(Location.timestamp.desc())
                .limit(limit)
            ).all()
        )

    def create(self, location: Location) -> Location:
        return self.add(location)

    def update(self, location: Location, **changes) -> Location:
        for key, value in changes.items():
            setattr(location, key, value)
        self.session.flush()
        self.session.commit()
        self.session.refresh(location)
        return location
