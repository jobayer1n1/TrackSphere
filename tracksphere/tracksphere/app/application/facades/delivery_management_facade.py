from datetime import datetime
from typing import Optional

from ..assignments.assignment_service import AssignmentService
from ..assignments.strategy import AssignmentStrategy, NearestDriverStrategy
from ..notifications import DeliveryAssignedEvent, DeliveryCancelledEvent, DeliveryCompletedEvent, DeliveryEventSource
from ..notifications.notification_decorator import (
    BasicNotification,
    LoggingDecorator,
    PriorityDecorator,
    TimestampDecorator,
)
from tracksphere.app.domain.deliveries.delivery_builder import DeliveryBuilder
from tracksphere.app.models import Delivery, DeliveryStatus, NotificationType, NotificationPriority, User
from tracksphere.app.repositories.assignments import AssignmentRepository
from tracksphere.app.repositories.delivery_repository import DeliveryRepository
from tracksphere.app.repositories.notification_repository import NotificationRepository
from tracksphere.app.repositories.driver_repository import DriverRepository


class DeliveryManagementFacade:
    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        assignment_repository: AssignmentRepository,
        notification_repository: NotificationRepository,
        driver_repository: DriverRepository,
        event_source: Optional[DeliveryEventSource] = None,
        assignment_strategy: Optional[AssignmentStrategy] = None,
    ):
        self.delivery_repository = delivery_repository
        self.assignment_repository = assignment_repository
        self.notification_repository = notification_repository
        self.driver_repository = driver_repository
        self.event_source = event_source or DeliveryEventSource()
        self.assignment_service = AssignmentService(
            strategy=assignment_strategy or NearestDriverStrategy(),
            assignment_repository=assignment_repository,
            event_source=self.event_source,
        )

    def create_delivery(
        self,
        pickup: str,
        destination: str,
        deadline: datetime,
        priority: int,
        vehicle_id: int,
        driver_id: int | None = None,
        notes: str | None = None,
    ) -> Delivery:
        builder = (
            DeliveryBuilder()
            .set_pickup(pickup)
            .set_destination(destination)
            .set_deadline(deadline)
            .set_priority(priority)
            .set_vehicle(vehicle_id)
        )
        if driver_id is not None:
            builder = builder.set_driver(driver_id)
        if notes is not None:
            builder = builder.set_notes(notes)

        delivery = builder.build()
        return self.delivery_repository.create(delivery)

    def assign_delivery(self, delivery_id: int) -> Delivery | None:
        delivery = self.delivery_repository.get(delivery_id)
        if not delivery:
            return None

        drivers = self.driver_repository.list()
        assignment = self.assignment_service.assign(delivery, drivers)
        self._create_assignment_notification(delivery, assignment.driver_id)
        return delivery

    def reassign_delivery(self, delivery_id: int, new_driver_id: int) -> Delivery | None:
        delivery = self.delivery_repository.get(delivery_id)
        if not delivery:
            return None

        driver = self.driver_repository.get(new_driver_id)
        if not driver:
            return None

        delivery.driver_id = new_driver_id
        delivery.status = DeliveryStatus.ASSIGNED
        self.delivery_repository.update(delivery)
        self._create_status_notification(delivery, "reassigned")
        return delivery

    def update_delivery_status(self, delivery_id: int, status: DeliveryStatus) -> Delivery | None:
        delivery = self.delivery_repository.get(delivery_id)
        if not delivery:
            return None

        old_status = delivery.status
        delivery.status = status
        self.delivery_repository.update(delivery)

        if status == DeliveryStatus.COMPLETED:
            event = DeliveryCompletedEvent(
                delivery_id=delivery.id,
                timestamp=datetime.utcnow(),
                event_type="completed",
                details="Delivery completed",
                previous_status=old_status,
                new_status=delivery.status,
            )
            self.event_source.notify(event)
        else:
            self._create_status_notification(delivery, "status_updated")

        return delivery

    def cancel_delivery(self, delivery_id: int) -> Delivery | None:
        delivery = self.delivery_repository.get(delivery_id)
        if not delivery:
            return None

        old_status = delivery.status
        delivery.status = DeliveryStatus.CANCELLED
        self.delivery_repository.update(delivery)

        event = DeliveryCancelledEvent(
            delivery_id=delivery.id,
            timestamp=datetime.utcnow(),
            event_type="cancelled",
            details="Delivery cancelled",
            previous_status=old_status,
            new_status=delivery.status,
        )
        self.event_source.notify(event)
        return delivery

    def get_delivery_summary(self, delivery_id: int) -> dict[str, object] | None:
        delivery = self.delivery_repository.get(delivery_id)
        if not delivery:
            return None

        return {
            "delivery_id": delivery.id,
            "status": delivery.status.value,
            "driver_id": delivery.driver_id,
            "vehicle_id": delivery.vehicle_id,
            "notes": delivery.notes,
        }

    def _create_assignment_notification(self, delivery: Delivery, driver_id: int) -> None:
        recipient = self._find_recipient_for_assignment(delivery)
        if not recipient:
            return

        notification = BasicNotification(
            recipient=recipient,
            message=f"Delivery {delivery.id} assigned to driver {driver_id}.",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
        )
        notification = PriorityDecorator(notification, NotificationPriority.HIGH)
        notification = TimestampDecorator(notification)
        notification = LoggingDecorator(notification)

        built = notification.build()
        self.notification_repository.create(built)

    def _create_status_notification(self, delivery: Delivery, action: str) -> None:
        recipient = self._find_recipient_for_assignment(delivery)
        if not recipient:
            return

        message = (
            f"Delivery {delivery.id} was {action}."
            if action == "reassigned"
            else f"Delivery {delivery.id} status is now {delivery.status.value}."
        )
        notification = BasicNotification(
            recipient=recipient,
            message=message,
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
        )
        notification = TimestampDecorator(notification)

        built = notification.build()
        self.notification_repository.create(built)

    def _find_recipient_for_assignment(self, delivery: Delivery) -> User | None:
        if delivery.driver_id is not None:
            driver = self.driver_repository.get(delivery.driver_id)
            return driver.user if driver else None
        return None
