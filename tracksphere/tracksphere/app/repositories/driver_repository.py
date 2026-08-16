from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import Driver
from .base import RepositoryBase


class DriverRepository(RepositoryBase[Driver]):
    def list(self) -> list[Driver]:
        return self.session.scalars(select(Driver)).all()

    def get(self, driver_id: int) -> Driver | None:
        return self.session.get(Driver, driver_id)

    def create(self, driver: Driver) -> Driver:
        return self.add(driver)

    def update(self, driver: Driver, **changes) -> Driver:
        for key, value in changes.items():
            setattr(driver, key, value)
        self.session.flush()
        return driver

    def delete(self, driver: Driver) -> None:
        super().delete(driver)
