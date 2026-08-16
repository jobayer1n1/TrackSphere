from __future__ import annotations
from datetime import datetime

from tracksphere.app.models import Delivery, DeliveryStatus
from .package_item import PackageGroup, Package, DeliveryItem


class DeliveryBuilderError(ValueError):
    pass


class DeliveryBuilder:
    def __init__(self) -> None:
        self._pickup: str | None = None
        self._destination: str | None = None
        self._deadline: datetime | None = None
        self._priority: int | None = None
        self._notes: str | None = None
        self._driver_id: int | None = None
        self._vehicle_id: int | None = None
        self._package_group: PackageGroup | None = None

    def set_pickup(self, pickup: str) -> DeliveryBuilder:
        self._pickup = pickup
        return self

    def set_destination(self, destination: str) -> DeliveryBuilder:
        self._destination = destination
        return self

    def set_deadline(self, deadline: datetime) -> DeliveryBuilder:
        self._deadline = deadline
        return self

    def set_priority(self, priority: int) -> DeliveryBuilder:
        self._priority = priority
        return self

    def set_notes(self, notes: str) -> DeliveryBuilder:
        self._notes = notes
        return self

    def set_driver(self, driver_id: int) -> DeliveryBuilder:
        self._driver_id = driver_id
        return self

    def set_vehicle(self, vehicle_id: int) -> DeliveryBuilder:
        self._vehicle_id = vehicle_id
        return self

    def set_package_group(self, package_group: PackageGroup) -> DeliveryBuilder:
        self._package_group = package_group
        return self

    def build(self) -> Delivery:
        if not self._pickup:
            raise DeliveryBuilderError("Delivery pickup is required")
        if not self._destination:
            raise DeliveryBuilderError("Delivery destination is required")
        if not self._deadline:
            raise DeliveryBuilderError("Delivery deadline is required")
        if self._priority is None:
            raise DeliveryBuilderError("Delivery priority is required")

        delivery = Delivery(
            pickup=self._pickup,
            destination=self._destination,
            deadline=self._deadline,
            priority=self._priority,
            status=DeliveryStatus.PENDING,
            notes=self._notes,
            driver_id=self._driver_id,
            vehicle_id=self._vehicle_id,
        )

        if self._package_group is not None:
            delivery.notes = f"{delivery.notes or ''}\nPackage summary: {self._package_group.describe()}".strip()

        return delivery
