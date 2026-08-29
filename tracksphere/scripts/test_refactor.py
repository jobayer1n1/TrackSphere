import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db
from app.models.enums import AvailabilityStatus, VehicleStatus, UserRole
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.delivery import Delivery
from app.core.locations.driver_location_adapter import DriverLocationAdapter, DriverNotAssignedError
from app.core.locations.location_service import TrackSphereLocationService
from app.core.locations.simulated_gps_adapter import SimulatedGPSAdapter
from app.core.locations.location_proxy import LocationServiceProxy
from app.core.assignment.strategies import (
    DefaultAvailabilityStrategy,
    HighPriorityStrategy,
    get_assignment_strategy,
)
from app.core.assignment.service import AssignmentService
from scripts.seed_data import seed

def run_tests():
    print("--- 1. Initializing & Seeding Database ---")
    seed()
    db = SessionLocal()

    try:
        provider = SimulatedGPSAdapter()
        service = TrackSphereLocationService(provider)

        print("\n--- 2. Testing DriverLocationAdapter (Adapter Pattern) ---")
        adapter = DriverLocationAdapter(service, db)

        # In seed data:
        # drv2 (Sarah Connor, driver_id=2) is assigned to Delivery 1 with Vehicle 2 (VAN-202)
        # drv1 (John Miller, driver_id=1) has completed delivery, now AVAILABLE, not assigned to any active delivery
        # drv3 (Alex Murphy, driver_id=3) is AVAILABLE, not assigned

        print("Testing assigned driver (Sarah Connor, ID=2)...")
        loc2 = adapter.get_driver_location(2)
        print(f"  Result: vehicle_id={loc2.vehicle_id}, lat={loc2.latitude}, lon={loc2.longitude}")
        assert loc2.vehicle_id == 2, f"Expected vehicle_id 2, got {loc2.vehicle_id}"
        print("  [PASS] Assigned driver successfully adapted to vehicle location.")

        # Find or use unassigned driver
        unassigned_driver = next(
            (d for d in db.query(Driver).all() if adapter.get_assigned_vehicle_id(d.id) is None),
            None
        )
        if unassigned_driver:
            print(f"Testing unassigned driver ({unassigned_driver.user.name if unassigned_driver.user else 'Driver'}, ID={unassigned_driver.id})...")
            try:
                adapter.get_driver_location(unassigned_driver.id)
                assert False, "Expected DriverNotAssignedError, but call succeeded!"
            except DriverNotAssignedError as e:
                print(f"  Caught expected DriverNotAssignedError: '{e}'")
                assert "Driver is not assigned to any vehicle" in str(e)
                print("  [PASS] Unassigned driver properly raises DriverNotAssignedError without dummy data.")

        print("\n--- 3. Testing LocationServiceProxy (Protection Proxy Pattern) ---")
        admin = db.query(User).filter(User.role == UserRole.ADMINISTRATOR).first()
        driver_user = db.query(User).filter(User.email == "driver.sarah@tracksphere.com").first()

        proxy_admin = LocationServiceProxy(service, admin, db=db)
        loc_admin_drv2 = proxy_admin.get_driver_location(2)
        assert loc_admin_drv2.vehicle_id == 2
        print("  [PASS] Admin can access driver location via proxy.")

        proxy_driver = LocationServiceProxy(service, driver_user, db=db)
        loc_driver_self = proxy_driver.get_driver_location()
        assert loc_driver_self.vehicle_id == 2
        print("  [PASS] Driver can access own assigned vehicle location via proxy.")

        try:
            proxy_driver.get_driver_location(1)  # unauthorized target driver
            assert False, "Expected PermissionError for driver accessing another driver"
        except PermissionError:
            print("  [PASS] Driver cannot access another driver's location.")

        print("\n--- 4. Testing Assignment Strategies (Strategy Pattern) ---")
        strat_default = get_assignment_strategy(strategy_name="default")
        assert isinstance(strat_default, DefaultAvailabilityStrategy)
        print("  [PASS] Resolved DefaultAvailabilityStrategy.")

        strat_high = get_assignment_strategy(strategy_name="high_priority")
        assert isinstance(strat_high, HighPriorityStrategy)
        print("  [PASS] Resolved HighPriorityStrategy by name.")

        strat_priority3 = get_assignment_strategy(priority=3)
        assert isinstance(strat_priority3, HighPriorityStrategy)
        print("  [PASS] Resolved HighPriorityStrategy by priority level >= 3.")

        # Test HighPriorityStrategy rule: Capacity >= 500kg
        test_driver = Driver(license_number="TEST-1", availability=AvailabilityStatus.AVAILABLE)
        small_vehicle = Vehicle(registration_number="TINY-1", capacity=300, status=VehicleStatus.AVAILABLE)
        large_vehicle = Vehicle(registration_number="BIG-1", capacity=3000, status=VehicleStatus.AVAILABLE)

        eligible_small, reason_small = strat_high.is_eligible(test_driver, small_vehicle)
        assert not eligible_small
        print(f"  [PASS] HighPriorityStrategy correctly rejected small vehicle: '{reason_small}'")

        eligible_large, reason_large = strat_high.is_eligible(test_driver, large_vehicle)
        assert eligible_large
        print(f"  [PASS] HighPriorityStrategy correctly accepted large vehicle: '{reason_large}'")

        print("\n==========================================")
        print("[SUCCESS] ALL BACKEND & DESIGN PATTERN TESTS PASSED!")
        print("==========================================")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
