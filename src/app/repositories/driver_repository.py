from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.driver import Driver
from app.repositories.base import RepositoryBase


class DriverRepository(RepositoryBase[Driver]):
    def list(self) -> List[Driver]:
        return list(self.session.scalars(select(Driver).options(joinedload(Driver.user)).order_by(Driver.id)).all())

    def get(self, driver_id: int) -> Optional[Driver]:
        return self.session.scalars(
            select(Driver).options(joinedload(Driver.user), joinedload(Driver.deliveries)).where(Driver.id == driver_id)
        ).first()

    def get_by_user_id(self, user_id: int) -> Optional[Driver]:
        return self.session.scalars(
            select(Driver).options(joinedload(Driver.user), joinedload(Driver.deliveries)).where(Driver.user_id == user_id)
        ).first()

    def get_by_license(self, license_number: str) -> Optional[Driver]:
        return self.session.scalars(select(Driver).where(Driver.license_number == license_number)).first()

    def create(self, driver: Driver) -> Driver:
        return self.add(driver)

    def update(self, driver: Driver, **changes) -> Driver:
        for key, value in changes.items():
            if value is not None:
                setattr(driver, key, value)
        self.session.flush()
        self.session.commit()
        self.session.refresh(driver)
        return driver
