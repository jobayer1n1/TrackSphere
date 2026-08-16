from fastapi.testclient import TestClient

from app.infrastructure.database import init_db
from tracksphere.main import app


client = TestClient(app)


def test_location_api_uses_proxy_and_adapter():
    init_db()
    login_response = client.post(
        "/login",
        data={"email": "dispatcher@tracksphere.local", "password": "dispatchpass"},
        follow_redirects=True,
    )
    assert login_response.status_code == 200

    response = client.get("/locations/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["vehicle_id"] == 1
    assert payload["latitude"] == 40.7128
    assert payload["longitude"] == -74.006


def test_all_vehicles_locations_api_endpoint():
    init_db()
    login_response = client.post(
        "/login",
        data={"email": "dispatcher@tracksphere.local", "password": "dispatchpass"},
        follow_redirects=True,
    )
    assert login_response.status_code == 200

    response = client.get("/locations/all_vehicles")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
    vehicle_ids = [item["vehicle_id"] for item in payload]
    assert 1 in vehicle_ids


def test_update_location_api_endpoint():
    init_db()
    sender_payload = {
        "vehicle_id": "BUS-001",
        "latitude": 23.8103,
        "longitude": 90.4125,
        "accuracy": 5.2,
        "altitude": 12.4,
        "speed": 8.3,
        "timestamp": "2026-08-15T18:45:00.000Z",
    }
    response = client.post("/locations/update/BUS-001", json=sender_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 23.8103
    assert data["longitude"] == 90.4125


