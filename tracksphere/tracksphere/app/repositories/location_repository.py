from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import Location
from .base import RepositoryBase


class LocationRepository(RepositoryBase[Location]):
    def list(self) -> list[Location]:
        return self.session.scalars(select(Location)).all()

    def get(self, location_id: int) -> Location | None:
        return self.session.get(Location, location_id)

    def create(self, location: Location) -> Location:
        return self.add(location)

    def update(self, location: Location, **changes) -> Location:
        for key, value in changes.items():
            setattr(location, key, value)
        self.session.flush()
        return location

    def delete(self, location: Location) -> None:
        super().delete(location)
