# TrackSphere Location & Telemetry Service

This document outlines the architecture and data flow for the GPS Telemetry and Location tracking system within TrackSphere.

## Overview
The location service manages real-time GPS tracking for vehicles and drivers. It bridges simulated hardware GPS feeds (via Adapters) through a secure Service Layer (via Proxies) down to the Database Layer, and broadcasts updates to the frontend in real-time via WebSockets.

## Design Patterns Used

TrackSphere uses standard GoF design patterns to keep the location service decoupled, scalable, and secure:

1. **Adapter Pattern** (`SimulatedGPSAdapter`, `DriverLocationAdapter`): 
   - *Problem Solved*: Incompatible data structures and varying hardware interfaces. 
   - *Target Interface*: `LocationProvider` / `DriverLocationProvider` (The common interfaces our system relies on).
   - *Adaptee*: External raw GPS device payloads, or underlying vehicle assignment logic (The incompatible interfaces/systems).
   - *Adapter*: `SimulatedGPSAdapter`, `DriverLocationAdapter` (The classes translating the Adaptee to match the Target Interface).
   - *Implementation*: Adapts external raw GPS feeds (or driver assignments) into our internal `TrackSphereLocation` domain model. This allows us to effortlessly swap out simulated GPS feeds for physical IoT hardware without touching any core business logic.
2. **Proxy Pattern (Protection Proxy)** (`LocationServiceProxy`):
   - *Problem Solved*: Security and cross-cutting access control.
   - *Implementation*: Wraps the core location service to intercept all location queries. It enforces Role-Based Access Control (RBAC) to ensure users can only track vehicles they are explicitly authorized to view, preventing unauthorized telemetry access.
3. **Observer Pattern** (`GPSTrackingSubject`, `WebSocketConnectionManager`):
   - *Problem Solved*: Tight coupling between state changes and external side effects.
   - *Implementation*: When a vehicle location is updated in the database, the subject fires a `LOCATION_UPDATE` event. The WebSocket manager (and Notification service) observes this and instantly pushes the update to frontend clients. The core tracking service itself knows absolutely nothing about WebSockets or user alerts.
4. **Dependency Injection (DI)**:
   - *Problem Solved*: Hardcoded dependencies making testing difficult.
   - *Implementation*: `LocationProvider` interfaces are injected into the core services. During automated testing, we can swap the live GPS adapter with a mock provider dynamically.

---

## Architecture Flow

The system strictly follows a layered architecture utilizing several GoF Design Patterns.

### 1. API Layer (`app/api/location_api.py`)
This layer handles standard REST HTTP requests and WebSocket connections.
- **Endpoints:**
  - `GET /api/locations/{vehicle_id}`: Fetch live coordinates for a specific vehicle.
  - `GET /api/locations/drivers/{driver_id}`: Fetch live coordinates for a driver (resolves to their assigned vehicle).
  - `POST /api/locations`: Manually push a GPS coordinate update.
  - `WS /api/locations/ws`: WebSocket endpoint that pushes real-time `LOCATION_UPDATE` events to the frontend.

### 2. Service Layer (`app/core/locations/`)
The service layer processes business logic, security, and hardware abstraction.
- **`LocationServiceProxy` (Protection Proxy Pattern):**
  - Intercepts all location requests from the API.
  - Checks if the current authenticated `User` has the required Role-Based Access Control (RBAC) permissions to view a specific vehicle or driver's location.
- **`TrackSphereLocationService`:**
  - The core domain service that processes valid requests passed down from the Proxy.
- **`SimulatedGPSAdapter` & `DriverLocationAdapter` (Adapter Pattern):**
  - **SimulatedGPSAdapter**: Acts as an interface to external hardware devices. It translates raw GPS hardware feeds into the internal `TrackSphereLocation` domain model.
  - **DriverLocationAdapter**: Resolves a driver's ID to their currently assigned vehicle, allowing the system to query "Where is Driver X?" rather than just "Where is Vehicle Y?".

### 3. Event Bus / Observer (`app/core/tracking/service.py`)
- **`GPSTrackingSubject` (Observer Pattern):**
  - A singleton event dispatcher. Whenever a valid location update occurs, it receives the data, persists it to the database, and immediately broadcasts a `LOCATION_UPDATE` event to all registered backend observers (such as the `NotificationService` and `WebSocketConnectionManager`).

### 4. Database Layer (`app/repositories/`)
- **`LocationRepository`**: Interacts with SQLAlchemy to persist historical GPS breadcrumbs (`app/models/location.py`).
- **`VehicleRepository` & `DriverRepository`**: Used for relational lookups (e.g., verifying if a vehicle exists or which vehicle a driver is assigned to).

---

## Class Explanations & Responsibilities

Why do we have so many classes just to handle a GPS coordinate? TrackSphere is built on SOLID principles and GoF design patterns to ensure the system is extensible (e.g., swapping simulated hardware for real hardware without rewriting business logic).

### 1. Data Structures & Models
- **`TrackSphereLocation` (Domain Model)**: Exists to provide a standardized, internal format for a GPS coordinate. It decouples the core logic from external payloads or database schemas.
- **`Location` (SQLAlchemy DB Model)**: Exists to map the concept of a location to a database table for historical storage.
- **`LocationCreate` / `LocationRead` (Pydantic Schemas)**: Exists to handle strict input validation and JSON serialization for the FastAPI endpoints.

### 2. Core Service Layer
- **`TrackSphereLocationService`**: The core business logic layer. It exists to abstract the underlying GPS hardware providers and give the API a simple, unified interface to request "Where is vehicle X?".
- **`LocationServiceProxy`**: Implements the Protection Proxy pattern. It exists to wrap the core service and strictly enforce Role-Based Access Control (RBAC). Without it, any user could query any vehicle's location by bypassing authorization checks.

### 3. Adapters & Hardware Interfaces
- **`LocationProvider`**: An abstract interface defining how GPS data should be fetched. It exists to enforce the Dependency Inversion principle.
- **`SimulatedGPSAdapter`**: Implements the Adapter pattern. It exists to simulate a real hardware GPS tracker. It transforms raw simulated payloads into the internal `TrackSphereLocation` model. If we switch to real GPS hardware tomorrow, we simply build a new adapter, and the rest of the application remains completely untouched.
- **`DriverLocationAdapter`**: Exists because drivers don't have GPS trackers on them; vehicles do. This adapter takes a request for a driver's location, figures out which vehicle they are assigned to, and translates it into a vehicle location request.

### 4. Real-Time Event System
- **`GPSTrackingSubject`**: Implements the Subject role of the Observer pattern. It exists to decouple the action of saving a location from the side effects (like sending notifications or updating WebSockets). 
- **`WebSocketConnectionManager`**: Acts as an Observer. It exists to safely bridge the synchronous event bus (`GPSTrackingSubject`) with the asynchronous WebSocket clients connected to the frontend.

---

## Sample Simulation: How the System Works

Here is a step-by-step walkthrough of what happens when a live location is updated and rendered on the user's screen.

### Step 1: External GPS Feed Updates
A GPS hardware device (or our API POST endpoint) sends a new coordinate payload for Vehicle `#2`.
```json
{
  "vehicle_id": 2,
  "latitude": 34.0522,
  "longitude": -118.2437
}
```

### Step 2: API Receives & Proxy Validates
1. The `POST /api/locations` endpoint receives the request.
2. It instantiates the `SimulatedGPSAdapter`, `TrackSphereLocationService`, and `LocationServiceProxy`.
3. The **Proxy** validates that the user submitting the data is authorized to track/update Vehicle `#2`.

### Step 3: Event Bus Broadcast & DB Persistence
1. The validated coordinates are passed to the `GPSTrackingSubject`.
2. The Subject calls the `LocationRepository` to `INSERT` the new coordinate into the PostgreSQL/SQLite database for historical tracking.
3. The Subject loops through its Observers and fires `.update("LOCATION_UPDATE", payload)`.

### Step 4: WebSocket Real-Time Push
1. The `WebSocketConnectionManager` (which is registered as an Observer) intercepts the update.
2. Because the Observer triggers synchronously, it safely pushes the payload into the `asyncio.Queue` belonging to the active WebSocket connection.
3. The `WS /api/locations/ws` endpoint running in the async event loop pulls from the queue and blasts the JSON payload to the user's browser.

### Step 5: Frontend Map Renders
1. The browser receives the WebSocket message in `app/static/js/map.js`.
2. Leaflet.js takes the new coordinates and instantly shifts the marker on the map for Vehicle `#2`, without needing a page refresh or HTTP polling!
