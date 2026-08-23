from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.vehicle import Vehicle
from app.repositories.base import RepositoryBase


class VehicleRepository(RepositoryBase[Vehicle]):
    def list(self) -> List[Vehicle]:
        return list(self.session.scalars(select(Vehicle).order_by(Vehicle.id)).all())

    def get(self, vehicle_id: int) -> Optional[Vehicle]:
        return self.session.scalars(
            select(Vehicle).options(joinedload(Vehicle.locations)).where(Vehicle.id == vehicle_id)
        ).first()

    def get_by_registration(self, registration_number: str) -> Optional[Vehicle]:
        return self.session.scalars(select(Vehicle).where(Vehicle.registration_number == registration_number)).first()

    def create(self, vehicle: Vehicle) -> Vehicle:
        return self.add(vehicle)

    def update(self, vehicle: Vehicle, **changes) -> Vehicle:
        for key, value in changes.items():
            if value is not None:
                setattr(vehicle, key, value)
        self.session.flush()
        self.session.commit()
        self.session.refresh(vehicle)
        return vehicle
