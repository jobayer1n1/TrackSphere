import sys
import threading
import time
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.core.auth.security import create_access_token

client = TestClient(app)

def test_websocket():
    print("Testing WebSocket broadcast via Observer pattern...")
    
    # Generate admin token
    admin_token = create_access_token({"sub": "1", "role": "ADMINISTRATOR", "email": "admin@tracksphere.com"})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # We will connect to the websocket
    try:
        with client.websocket_connect("/api/locations/ws") as websocket:
            print("  [PASS] WebSocket connected successfully.")
            
            # We trigger an update in a separate thread to simulate concurrent client pushing location
            def trigger_update():
                time.sleep(0.5)
                print("  Triggering location update via POST /api/locations...")
                payload = {
                    "vehicle_id": 2,
                    "latitude": 45.123,
                    "longitude": -75.123,
                    "timestamp": "2026-08-25T10:00:00Z"
                }
                res = client.post("/api/locations", json=payload, headers=headers)
                if res.status_code != 201:
                    print(f"  [ERROR] POST failed: {res.status_code} {res.text}")
                
            t = threading.Thread(target=trigger_update)
            t.start()
            
            # Wait for WS message
            data = websocket.receive_json()
            print("  Received WS payload:", data)
            
            assert data["vehicle_id"] == 2
            assert data["latitude"] == 45.123
            print("  [PASS] WebSocket received location update in real-time.")
            t.join()
            print("All tests passed.")
    except Exception as e:
        print(f"  [FAIL] WebSocket test failed: {e}")

if __name__ == "__main__":
    test_websocket()
