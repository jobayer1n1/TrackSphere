from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import Vehicle
from .base import RepositoryBase


class VehicleRepository(RepositoryBase[Vehicle]):
    def list(self) -> list[Vehicle]:
        return self.session.scalars(select(Vehicle)).all()

    def get(self, vehicle_id: int) -> Vehicle | None:
        return self.session.get(Vehicle, vehicle_id)

    def create(self, vehicle: Vehicle) -> Vehicle:
        return self.add(vehicle)

    def update(self, vehicle: Vehicle, **changes) -> Vehicle:
        for key, value in changes.items():
            setattr(vehicle, key, value)
        self.session.flush()
        return vehicle

    def delete(self, vehicle: Vehicle) -> None:
        super().delete(vehicle)
