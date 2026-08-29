from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.delivery import Delivery
from app.models.enums import DeliveryStatus
from app.repositories.base import RepositoryBase


class DeliveryRepository(RepositoryBase[Delivery]):
    def list(self) -> List[Delivery]:
        return list(
            self.session.scalars(
                select(Delivery)
                .options(joinedload(Delivery.driver), joinedload(Delivery.vehicle))
                .order_by(Delivery.created_at.desc())
            ).all()
        )

    def get(self, delivery_id: int) -> Optional[Delivery]:
        return self.session.scalars(
            select(Delivery)
            .options(joinedload(Delivery.driver), joinedload(Delivery.vehicle), joinedload(Delivery.assignments))
            .where(Delivery.id == delivery_id)
        ).first()

    def list_by_driver(self, driver_id: int) -> List[Delivery]:
        return list(
            self.session.scalars(
                select(Delivery)
                .options(joinedload(Delivery.vehicle))
                .where(Delivery.driver_id == driver_id)
                .order_by(Delivery.created_at.desc())
            ).all()
        )

    def list_by_status(self, status: DeliveryStatus) -> List[Delivery]:
        return list(
            self.session.scalars(
                select(Delivery)
                .options(joinedload(Delivery.driver), joinedload(Delivery.vehicle))
                .where(Delivery.status == status)
                .order_by(Delivery.created_at.desc())
            ).all()
        )

    def create(self, delivery: Delivery) -> Delivery:
        return self.add(delivery)

    def update(self, delivery: Delivery, **changes) -> Delivery:
        for key, value in changes.items():
            if value is not None:
                setattr(delivery, key, value)
        self.session.flush()
        self.session.commit()
        self.session.refresh(delivery)
        return delivery
