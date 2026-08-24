import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.core.auth.security import create_access_token

client = TestClient(app)

def test_api():
    print("Testing API endpoints...")

    # Generate admin token (User ID 1 in seed)
    admin_token = create_access_token({"sub": "1", "role": "ADMINISTRATOR", "email": "admin@tracksphere.com"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Vehicle location
    res_veh = client.get("/api/locations/2", headers=headers)
    assert res_veh.status_code == 200, f"Expected 200, got {res_veh.status_code}: {res_veh.text}"
    data_veh = res_veh.json()
    assert data_veh["vehicle_id"] == 2
    print("  [PASS] GET /api/locations/2 returned valid vehicle coordinates.")

    # 2. Driver location for assigned driver (Sarah Connor, ID=2)
    res_drv_assigned = client.get("/api/locations/drivers/2", headers=headers)
    assert res_drv_assigned.status_code == 200, f"Expected 200, got {res_drv_assigned.status_code}: {res_drv_assigned.text}"
    data_drv = res_drv_assigned.json()
    assert data_drv["vehicle_id"] == 2
    assert "Sarah Connor" in data_drv["driver_name"]
    print("  [PASS] GET /api/locations/drivers/2 returned assigned vehicle location via DriverLocationAdapter.")

    # 3. Create a test unassigned driver to test unassigned driver resolution
    from app.database import SessionLocal
    from app.models.driver import Driver
    from app.models.user import User
    from app.models.enums import AvailabilityStatus, UserRole
    from app.core.auth.security import hash_password

    db = SessionLocal()
    unassigned_user = db.query(User).filter(User.email == "test.unassigned@tracksphere.com").first()
    if not unassigned_user:
        unassigned_user = User(
            name="Test Unassigned Driver",
            email="test.unassigned@tracksphere.com",
            password_hash=hash_password("test123"),
            role=UserRole.DRIVER,
            active=True
        )
        db.add(unassigned_user)
        db.commit()
        db.refresh(unassigned_user)
        unassigned_drv = Driver(
            user_id=unassigned_user.id,
            license_number="CDL-TEST-0001",
            availability=AvailabilityStatus.AVAILABLE
        )
        db.add(unassigned_drv)
        db.commit()
        db.refresh(unassigned_drv)
    else:
        unassigned_drv = db.query(Driver).filter(Driver.user_id == unassigned_user.id).first()

    unassigned_driver_id = unassigned_drv.id
    db.close()

    # Test driver location for unassigned driver
    res_drv_unassigned = client.get(f"/api/locations/drivers/{unassigned_driver_id}", headers=headers)
    assert res_drv_unassigned.status_code == 404, f"Expected 404, got {res_drv_unassigned.status_code}"
    assert "Driver is not assigned to any vehicle" in res_drv_unassigned.json()["detail"]
    print(f"  [PASS] GET /api/locations/drivers/{unassigned_driver_id} returned 404 with 'Driver is not assigned to any vehicle'.")

    # 4. Search endpoint for driver
    res_search_drv_assigned = client.get("/api/locations/search?type=driver&id=2", headers=headers)
    assert res_search_drv_assigned.status_code == 200
    data_s1 = res_search_drv_assigned.json()
    assert data_s1["is_assigned"] is True
    assert data_s1["vehicle_id"] == 2
    print("  [PASS] GET /api/locations/search?type=driver&id=2 returned is_assigned=True.")

    res_search_drv_unassigned = client.get(f"/api/locations/search?type=driver&id={unassigned_driver_id}", headers=headers)
    assert res_search_drv_unassigned.status_code == 200
    data_s2 = res_search_drv_unassigned.json()
    assert data_s2["is_assigned"] is False
    assert data_s2["message"] == "Driver is not assigned to any vehicle."
    print(f"  [PASS] GET /api/locations/search?type=driver&id={unassigned_driver_id} returned is_assigned=False with descriptive message.")

    # 5. Search endpoint for vehicle
    res_search_veh = client.get("/api/locations/search?type=vehicle&id=1", headers=headers)
    assert res_search_veh.status_code == 200
    data_s3 = res_search_veh.json()
    assert data_s3["target_type"] == "vehicle"
    assert data_s3["vehicle_id"] == 1
    print("  [PASS] GET /api/locations/search?type=vehicle&id=1 returned vehicle coordinates.")

    # 6. HTML page tests for Admin, Dispatcher, and Driver
    driver_sarah_token = create_access_token({"sub": "4", "role": "DRIVER", "email": "driver.sarah@tracksphere.com"})
    driver_alex_token = create_access_token({"sub": "5", "role": "DRIVER", "email": "driver.alex@tracksphere.com"})
    dispatcher_token = create_access_token({"sub": "2", "role": "DISPATCHER", "email": "dispatcher@tracksphere.com"})

    # Test vehicle-locations HTML route for Admin
    client.cookies.set("tracksphere_session", admin_token)
    res_html_admin = client.get("/vehicle-locations")
    assert res_html_admin.status_code == 200, f"Expected 200 for Admin /vehicle-locations, got {res_html_admin.status_code}"
    print("  [PASS] GET /vehicle-locations rendered successfully for Admin.")

    # Test vehicle-locations HTML route for Dispatcher
    client.cookies.set("tracksphere_session", dispatcher_token)
    res_html_dispatch = client.get("/vehicle-locations")
    assert res_html_dispatch.status_code == 200, f"Expected 200 for Dispatcher /vehicle-locations, got {res_html_dispatch.status_code}"
    print("  [PASS] GET /vehicle-locations rendered successfully for Dispatcher.")

    # Test vehicle-locations HTML route for Driver (Sarah Connor - assigned)
    client.cookies.set("tracksphere_session", driver_sarah_token)
    res_html_drv_assigned = client.get("/vehicle-locations")
    assert res_html_drv_assigned.status_code == 200, f"Expected 200 for Driver (Sarah) /vehicle-locations, got {res_html_drv_assigned.status_code}"
    print("  [PASS] GET /vehicle-locations rendered successfully for assigned Driver (Sarah Connor).")

    # Test vehicle-locations HTML route for Driver (Alex Murphy - unassigned)
    client.cookies.set("tracksphere_session", driver_alex_token)
    res_html_drv_unassigned = client.get("/vehicle-locations")
    assert res_html_drv_unassigned.status_code == 200, f"Expected 200 for Driver (Alex) /vehicle-locations, got {res_html_drv_unassigned.status_code}"
    print("  [PASS] GET /vehicle-locations rendered successfully for unassigned Driver (Alex Murphy).")

    print("\n==========================================")
    print("[SUCCESS] ALL API & WEB ROUTE TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    test_api()
