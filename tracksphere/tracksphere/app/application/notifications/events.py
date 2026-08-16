from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tracksphere.app.models import Delivery, DeliveryStatus


@dataclass(frozen=True)
class DeliveryEvent:
    delivery_id: int
    timestamp: datetime
    event_type: str
    details: str


@dataclass(frozen=True)
class DeliveryAssignedEvent(DeliveryEvent):
    driver_id: int
    vehicle_id: int | None


@dataclass(frozen=True)
class DeliveryStatusChangedEvent(DeliveryEvent):
    previous_status: DeliveryStatus
    new_status: DeliveryStatus


@dataclass(frozen=True)
class DeliveryCompletedEvent(DeliveryStatusChangedEvent):
    pass


@dataclass(frozen=True)
class DeliveryCancelledEvent(DeliveryStatusChangedEvent):
    pass
