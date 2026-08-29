# TrackSphere: Fleet & Delivery Management System

**TrackSphere** is a modular web platform designed for courier and fleet logistics operations, featuring centralized fleet management, automated job dispatching, real-time GPS telemetry tracking, and strict Role-Based Access Control (RBAC).

---

## 🛠️ Technology Stack
- **Backend:** FastAPI (Python 3.10+) with Uvicorn
- **Frontend:** Semantic HTML5, Vanilla CSS3 Custom Design System (Space Grotesk, Inter, dark slate theme), Vanilla JavaScript, and Leaflet.js interactive maps. *(No React/JS framework required)*
- **Database:** SQLite with SQLAlchemy ORM (Repository Pattern)

---

## 🏛️ Object-Oriented Design Patterns Applied

| # | Design Pattern | Component / File | Architectural Role |
|---|---|---|---|
| 1 | **Inheritance** | [`app/core/users/base.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/users/base.py) &rarr; `Administrator`, `Dispatcher`, `DriverUser` | Domain user hierarchy establishing common identity and role-specific permission scopes. |
| 2 | **Factory Method** | [`app/core/users/factory.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/users/factory.py) (`UserFactory`) | Dynamically instantiates concrete `User` subclass objects based on `UserRole`. |
| 3 | **Singleton** | [`app/core/auth/service.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/auth/service.py) & [`app/core/notifications/service.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/notifications/service.py) | Centralized, thread-safe singletons managing authentication sessions and system broadcasts. |
| 4 | **Proxy (Protection Proxy)** | [`app/core/locations/location_proxy.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/locations/location_proxy.py) (`LocationServiceProxy`) | Enforces strict RBAC on GPS telemetry: Admins & Dispatchers view all vehicles; Drivers can only access their assigned unit. |
| 5 | **Adapter** | [`app/core/locations/driver_location_adapter.py`](file:///c:/Users/ttt/Desktop/cse327finaldemo/TrackSphere/tracksphere/app/core/locations/driver_location_adapter.py) (`DriverLocationAdapter`), [`app/core/locations/simulated_gps_adapter.py`](file:///c:/Users/ttt/Desktop/cse327finaldemo/TrackSphere/tracksphere/app/core/locations/simulated_gps_adapter.py), & [`app/core/notifications/channels.py`](file:///c:/Users/ttt/Desktop/cse327finaldemo/TrackSphere/tracksphere/app/core/notifications/channels.py) | Adapts driver location queries to underlying vehicle GPS feeds (`DriverLocationAdapter`), and standardizes hardware feeds into canonical `TrackSphereLocation`. |
| 6 | **Strategy** | [`app/core/assignment/strategies.py`](file:///c:/Users/ttt/Desktop/cse327finaldemo/TrackSphere/tracksphere/app/core/assignment/strategies.py) (`AssignmentStrategy`, `DefaultAvailabilityStrategy`, `HighPriorityStrategy`) | Pluggable algorithm verifying driver availability and vehicle constraints (e.g., minimum capacity checks for high-priority dispatches). |
| 7 | **Observer** | [`app/core/tracking/service.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/tracking/service.py) (`GPSTrackingSubject`, `Observer`) | Broadcasts live telemetry updates to registered notification and dashboard observers. |
| 8 | **Decorator** | [`app/core/notifications/decorators.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/notifications/decorators.py) (`NotificationDecorator`) | Dynamically enriches raw messages with in-app priority badges or email-style headers. |
| 9 | **Facade** | [`app/core/facade/dashboard_facade.py`](file:///c:/Users/ttt/Desktop/CSE%20327%20Project%20Final%20Demo/app/core/facade/dashboard_facade.py) (`DashboardFacade`) | Synthesizes metrics and datasets across user, fleet, delivery, and notification repositories into role-tailored dashboard summaries. |

---

## 📁 Directory Structure

```
TrackSphere/
├── app/
│   ├── main.py                  # FastAPI app entrypoint, static & template mounting
│   ├── config.py                # App configuration & settings
│   ├── database.py              # SQLite engine, session maker, Base, init_db()
│   ├── models/                  # SQLAlchemy ORM Models (User, Driver, Vehicle, Delivery, Assignment, Location, Notification)
│   ├── schemas/                 # Pydantic validation schemas
│   ├── repositories/            # Data Access Layer (Repository Pattern)
│   ├── core/                    # Clean OOP & Design Patterns
│   │   ├── users/               # [1] Inheritance & [2] Factory Method
│   │   ├── auth/                # [3] Singleton Authentication
│   │   ├── locations/           # [4] Proxy & [5] Adapter Patterns
│   │   ├── assignment/          # [6] Strategy Pattern
│   │   ├── tracking/            # [7] Observer Pattern
│   │   ├── notifications/       # [3] Singleton, [8] Decorator, [5] Adapter Patterns
│   │   └── facade/              # [9] Facade Pattern
│   ├── api/                     # REST API & HTML View Controllers
│   ├── templates/               # Semantic HTML5 Templates (Jinja2)
│   └── static/                  # Vanilla CSS Design System & Leaflet JS Map Engine
├── data/
│   └── tracksphere.db           # SQLite database
├── scripts/
│   └── seed_data.py             # Database initialization and demo seeder
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Set Up Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Seed Demo Database
```bash
python scripts/seed_data.py
```

### 3. Start Application Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser at `http://127.0.0.1:8000`.

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Access Scope |
|---|---|---|---|
| **Administrator** | `admin@tracksphere.com` | `admin123` | Full access across all modules, fleet oversight, and global telemetry. |
| **Dispatcher** | `dispatcher@tracksphere.com` | `dispatch123` | Create deliveries, assign driver/vehicle pairs, view live fleet GPS map. |
| **Driver** | `driver.sarah@tracksphere.com` | `driver123` | View active assigned job, update transit status, inspect assigned vehicle GPS. |
| **Driver** | `driver.john@tracksphere.com` | `driver123` | View assigned job queue and notifications. |
