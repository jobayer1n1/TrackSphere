from datetime import datetime
from typing import List, Optional

from .strategy import AssignmentStrategy
from ..notifications import DeliveryAssignedEvent, DeliveryEventSource
from tracksphere.app.models import Delivery, DeliveryStatus, Driver
from tracksphere.app.repositories.assignments import AssignmentRepository


class AssignmentError(Exception):
    pass


class AssignmentService:
    """Assigns deliveries using a configurable strategy."""

    def __init__(
        self,
        strategy: AssignmentStrategy,
        assignment_repository: AssignmentRepository,
        event_source: Optional[DeliveryEventSource] = None,
    ):
        self.strategy = strategy
        self.assignment_repository = assignment_repository
        self.event_source = event_source

    def assign(self, delivery: Delivery, drivers: List[Driver]):
        driver = self.strategy.select_driver(delivery, drivers)
        if not driver:
            raise AssignmentError("No suitable driver available for assignment")

        delivery.status = DeliveryStatus.ASSIGNED
        delivery.driver_id = driver.id
        assignment = self.assignment_repository.create_assignment(delivery_id=delivery.id, driver_id=driver.id)

        if self.event_source is not None:
            event = DeliveryAssignedEvent(
                delivery_id=delivery.id,
                timestamp=datetime.utcnow(),
                event_type="assigned",
                details="Delivery assigned",
                driver_id=driver.id,
                vehicle_id=delivery.vehicle_id,
            )
            self.event_source.notify(event)

        return assignment

    def set_strategy(self, strategy: AssignmentStrategy):
        self.strategy = strategy
