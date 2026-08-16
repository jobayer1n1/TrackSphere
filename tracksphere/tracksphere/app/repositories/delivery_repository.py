from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import Delivery
from .base import RepositoryBase


class DeliveryRepository(RepositoryBase[Delivery]):
    def list(self) -> list[Delivery]:
        return self.session.scalars(select(Delivery)).all()

    def get(self, delivery_id: int) -> Delivery | None:
        return self.session.get(Delivery, delivery_id)

    def create(self, delivery: Delivery) -> Delivery:
        return self.add(delivery)

    def update(self, delivery: Delivery, **changes) -> Delivery:
        for key, value in changes.items():
            setattr(delivery, key, value)
        self.session.flush()
        return delivery

    def delete(self, delivery: Delivery) -> None:
        super().delete(delivery)
