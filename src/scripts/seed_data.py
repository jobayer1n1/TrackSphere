"""
TrackSphere Database Seeder
Populates initial demo accounts, fleet vehicles, drivers, deliveries, and telemetry.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.auth.security import hash_password
from app.database import Base, SessionLocal, engine, init_db
from app.models.assignment import Assignment
from app.models.delivery import Delivery
from app.models.driver import Driver
from app.models.enums import (
    AssignmentStatus,
    AvailabilityStatus,
    DeliveryStatus,
    NotificationPriority,
    NotificationType,
    UserRole,
    VehicleStatus,
)
from app.models.location import Location
from app.models.notification import Notification
from app.models.user import User
from app.models.vehicle import Vehicle


def seed():
    print("Initializing SQLite schema...")
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding Users...")
        admin = User(
            name="Elena Vance (Admin)",
            email="admin@tracksphere.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMINISTRATOR,
            active=True,
        )
        dispatcher = User(
            name="Marcus Kane (Dispatcher)",
            email="dispatcher@tracksphere.com",
            password_hash=hash_password("dispatch123"),
            role=UserRole.DISPATCHER,
            active=True,
        )
        user_driver1 = User(
            name="John Miller (Driver)",
            email="driver.john@tracksphere.com",
            password_hash=hash_password("driver123"),
            role=UserRole.DRIVER,
            active=True,
        )
        user_driver2 = User(
            name="Sarah Connor (Driver)",
            email="driver.sarah@tracksphere.com",
            password_hash=hash_password("driver123"),
            role=UserRole.DRIVER,
            active=True,
        )
        user_driver3 = User(
            name="Alex Murphy (Driver)",
            email="driver.alex@tracksphere.com",
            password_hash=hash_password("driver123"),
            role=UserRole.DRIVER,
            active=True,
        )
        db.add_all([admin, dispatcher, user_driver1, user_driver2, user_driver3])
        db.commit()

        print("Seeding Drivers...")
        drv1 = Driver(
            user_id=user_driver1.id,
            license_number="CDL-NY-89102",
            availability=AvailabilityStatus.AVAILABLE,
        )
        drv2 = Driver(
            user_id=user_driver2.id,
            license_number="CDL-CA-44512",
            availability=AvailabilityStatus.UNAVAILABLE,
        )
        drv3 = Driver(
            user_id=user_driver3.id,
            license_number="CDL-IL-90214",
            availability=AvailabilityStatus.AVAILABLE,
        )
        db.add_all([drv1, drv2, drv3])
        db.commit()

        print("Seeding Vehicles...")
        v1 = Vehicle(
            registration_number="TRK-101",
            vehicle_type="Heavy Duty Truck",
            capacity=4500,
            status=VehicleStatus.AVAILABLE,
        )
        v2 = Vehicle(
            registration_number="VAN-202",
            vehicle_type="Express Courier Van",
            capacity=1200,
            status=VehicleStatus.ASSIGNED,
        )
        v3 = Vehicle(
            registration_number="VAN-303",
            vehicle_type="Electric Cargo Van",
            capacity=1500,
            status=VehicleStatus.AVAILABLE,
        )
        v4 = Vehicle(
            registration_number="TRK-404",
            vehicle_type="Medium Freight Van",
            capacity=2800,
            status=VehicleStatus.AVAILABLE,
        )
        db.add_all([v1, v2, v3, v4])
        db.commit()

        print("Seeding Deliveries & Assignments...")
        now = datetime.now(timezone.utc)
        
        # Delivery 1: In progress by Sarah Connor with VAN-202
        d1 = Delivery(
            pickup="Manhattan Port, Terminal 3",
            destination="Midtown Commercial Center",
            deadline=now + timedelta(hours=4),
            priority=3,
            status=DeliveryStatus.IN_PROGRESS,
            driver_id=drv2.id,
            vehicle_id=v2.id,
            notes="Fragile electronic parts; handle with care.",
        )
        # Delivery 2: Pending assignment
        d2 = Delivery(
            pickup="JFK Cargo Complex, Bay 14",
            destination="Brooklyn Distribution Hub",
            deadline=now + timedelta(hours=12),
            priority=2,
            status=DeliveryStatus.PENDING,
            notes="Palletized medical inventory.",
        )
        # Delivery 3: Pending assignment
        d3 = Delivery(
            pickup="Newark Fulfillment Center",
            destination="Queens Retail Depot",
            deadline=now + timedelta(hours=18),
            priority=1,
            status=DeliveryStatus.PENDING,
            notes="Standard ground shipping.",
        )
        # Delivery 4: Completed
        d4 = Delivery(
            pickup="Long Island Logistics Park",
            destination="Bronx Medical Center",
            deadline=now - timedelta(hours=2),
            priority=3,
            status=DeliveryStatus.COMPLETED,
            driver_id=drv1.id,
            vehicle_id=v1.id,
            notes="Completed on schedule.",
        )
        db.add_all([d1, d2, d3, d4])
        db.commit()

        # Assignment record for Delivery 1
        assign1 = Assignment(
            delivery_id=d1.id,
            driver_id=drv2.id,
            vehicle_id=v2.id,
            assigned_at=now - timedelta(hours=1),
            status=AssignmentStatus.CONFIRMED,
        )
        db.add(assign1)
        db.commit()

        print("Seeding Initial GPS Telemetry...")
        loc1 = Location(vehicle_id=v1.id, latitude=40.7128, longitude=-74.0060, timestamp=now)
        loc2 = Location(vehicle_id=v2.id, latitude=34.0522, longitude=-118.2437, timestamp=now)
        loc3 = Location(vehicle_id=v3.id, latitude=41.8781, longitude=-87.6298, timestamp=now)
        loc4 = Location(vehicle_id=v4.id, latitude=29.7604, longitude=-95.3698, timestamp=now)
        db.add_all([loc1, loc2, loc3, loc4])
        db.commit()

        print("Seeding Notifications...")
        n1 = Notification(
            recipient_id=admin.id,
            message="System initialized with 4 fleet vehicles and 3 active driver profiles.",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
            read=False,
            timestamp=now,
        )
        n2 = Notification(
            recipient_id=user_driver2.id,
            message="[HIGH] You have been assigned to Delivery #1: Manhattan Port -> Midtown Commercial Center.",
            notification_type=NotificationType.ALERT,
            priority=NotificationPriority.HIGH,
            read=False,
            timestamp=now - timedelta(hours=1),
        )
        n3 = Notification(
            recipient_id=dispatcher.id,
            message="[MEDIUM] Delivery #2 (JFK Cargo Complex) is in the dispatch queue awaiting assignment.",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
            read=False,
            timestamp=now,
        )
        db.add_all([n1, n2, n3])
        db.commit()

        print("\nSeed completed successfully!")
        print("------------------------------------------")
        print("Demo Credentials:")
        print("1. Administrator: admin@tracksphere.com / admin123")
        print("2. Dispatcher:    dispatcher@tracksphere.com / dispatch123")
        print("3. Driver:        driver.sarah@tracksphere.com / driver123")
        print("4. Driver:        driver.john@tracksphere.com / driver123")
        print("------------------------------------------")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
