from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session

from app.models.enums import AvailabilityStatus, DeliveryStatus, VehicleStatus
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vehicle_repository import VehicleRepository


class DashboardFacade:
    """
    Facade Pattern:
    Provides a unified, simplified interface to synthesize and aggregate metrics, fleet statuses,
    deliveries, and notifications across disparate repository subsystems for each user role.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.driver_repo = DriverRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.delivery_repo = DeliveryRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.location_repo = LocationRepository(db)

    def get_administrator_summary(self) -> dict[str, Any]:
        """Synthesize global operational KPIs for Administrator."""
        users = self.user_repo.list()
        drivers = self.driver_repo.list()
        vehicles = self.vehicle_repo.list()
        deliveries = self.delivery_repo.list()

        total_deliveries = len(deliveries)
        active_deliveries = sum(
            1 for d in deliveries if d.status in [DeliveryStatus.ASSIGNED, DeliveryStatus.IN_PROGRESS]
        )
        completed_deliveries = sum(1 for d in deliveries if d.status == DeliveryStatus.COMPLETED)
        available_vehicles = sum(1 for v in vehicles if v.status == VehicleStatus.AVAILABLE)
        available_drivers = sum(1 for d in drivers if d.availability == AvailabilityStatus.AVAILABLE)

        return {
            "role": "ADMINISTRATOR",
            "kpi": {
                "total_users": len(users),
                "total_drivers": len(drivers),
                "available_drivers": available_drivers,
                "total_vehicles": len(vehicles),
                "available_vehicles": available_vehicles,
                "total_deliveries": total_deliveries,
                "active_deliveries": active_deliveries,
                "completed_deliveries": completed_deliveries,
            },
            "recent_deliveries": deliveries[:5],
            "vehicles": vehicles,
            "drivers": drivers,
        }

    def get_dispatcher_summary(self) -> dict[str, Any]:
        """Synthesize dispatch queue and driver-vehicle availability for Dispatcher."""
        deliveries = self.delivery_repo.list()
        drivers = self.driver_repo.list()
        vehicles = self.vehicle_repo.list()

        pending_deliveries = [d for d in deliveries if d.status == DeliveryStatus.PENDING]
        active_deliveries = [
            d for d in deliveries if d.status in [DeliveryStatus.ASSIGNED, DeliveryStatus.IN_PROGRESS]
        ]
        available_drivers = [d for d in drivers if d.availability == AvailabilityStatus.AVAILABLE]
        available_vehicles = [v for v in vehicles if v.status == VehicleStatus.AVAILABLE]

        return {
            "role": "DISPATCHER",
            "kpi": {
                "pending_queue_count": len(pending_deliveries),
                "active_transit_count": len(active_deliveries),
                "ready_drivers_count": len(available_drivers),
                "ready_vehicles_count": len(available_vehicles),
            },
            "pending_deliveries": pending_deliveries,
            "active_deliveries": active_deliveries,
            "available_drivers": available_drivers,
            "available_vehicles": available_vehicles,
        }

    def get_driver_summary(self, user_id: int) -> dict[str, Any]:
        """Synthesize assigned jobs and route details for Driver."""
        driver = self.driver_repo.get_by_user_id(user_id)
        if not driver:
            return {
                "role": "DRIVER",
                "driver": None,
                "assigned_deliveries": [],
                "active_delivery": None,
                "notifications": self.notification_repo.list_by_user(user_id),
            }

        assigned_deliveries = self.delivery_repo.list_by_driver(driver.id)
        active_delivery = next(
            (d for d in assigned_deliveries if d.status in [DeliveryStatus.ASSIGNED, DeliveryStatus.IN_PROGRESS]),
            None,
        )

        return {
            "role": "DRIVER",
            "driver": driver,
            "assigned_deliveries": assigned_deliveries,
            "active_delivery": active_delivery,
            "notifications": self.notification_repo.list_by_user(user_id)[:10],
        }
