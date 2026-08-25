import asyncio
from typing import Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.locations.driver_location_adapter import DriverLocationAdapter, DriverNotAssignedError
from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_proxy import LocationServiceProxy
from app.core.locations.location_service import TrackSphereLocationService
from app.core.locations.simulated_gps_adapter import SimulatedGPSAdapter
from app.core.tracking.service import tracking_subject, Observer
from app.models.user import User
from app.repositories.driver_repository import DriverRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.location import (
    DriverLocationRead,
    LocationCreate,
    LocationRead,
    LocationSearchResult,
)

router = APIRouter(prefix="/api/locations", tags=["Location & GPS Telemetry"])


@router.get("/driver/me", response_model=DriverLocationRead)
def get_my_driver_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve live telemetry for the current authenticated driver.
    Uses DriverLocationAdapter (Adapter Pattern) to resolve assigned vehicle location.
    If the driver is not assigned to any vehicle, returns 404.
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user, db=db)

    try:
        location = proxy.get_driver_location()
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except DriverNotAssignedError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    # Persist and notify observers via GPSTrackingSubject
    tracking_subject.receive_location_update(db, location)

    driver = current_user.driver
    vehicle_repo = VehicleRepository(db)
    vehicle = vehicle_repo.get(location.vehicle_id) if location.vehicle_id else None

    return DriverLocationRead(
        driver_id=driver.id if driver else 0,
        driver_name=current_user.name,
        vehicle_id=location.vehicle_id,
        vehicle_registration=vehicle.registration_number if vehicle else f"Vehicle #{location.vehicle_id}",
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=location.timestamp,
    )


@router.get("/drivers/{driver_id}", response_model=DriverLocationRead)
def get_driver_location(
    driver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve live telemetry for a specific driver.
    Uses DriverLocationAdapter (Adapter Pattern) to resolve assigned vehicle location.
    If the driver is not assigned to any vehicle, returns 404.
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user, db=db)

    try:
        location = proxy.get_driver_location(driver_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except DriverNotAssignedError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    # Persist and notify observers via GPSTrackingSubject
    tracking_subject.receive_location_update(db, location)

    driver = DriverRepository(db).get(driver_id)
    vehicle = VehicleRepository(db).get(location.vehicle_id) if location.vehicle_id else None

    return DriverLocationRead(
        driver_id=driver_id,
        driver_name=driver.user.name if driver and driver.user else f"Driver #{driver_id}",
        vehicle_id=location.vehicle_id,
        vehicle_registration=vehicle.registration_number if vehicle else f"Vehicle #{location.vehicle_id}",
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=location.timestamp,
    )


@router.get("/search", response_model=LocationSearchResult)
def search_location(
    type: str = Query("vehicle", pattern="^(vehicle|driver)$"),
    id: int | None = Query(None),
    q: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unified search endpoint for live telemetry by Vehicle or Driver.
    - If Driver: Uses DriverLocationAdapter. If assigned, returns assigned vehicle coordinates;
      if unassigned, returns result with is_assigned=False and descriptive message.
    - If Vehicle: Returns vehicle live coordinates.
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user, db=db)

    if type == "vehicle":
        vehicle_repo = VehicleRepository(db)
        target_vehicle = None
        if id is not None:
            target_vehicle = vehicle_repo.get(id)
        elif q:
            all_vehicles = vehicle_repo.list()
            q_lower = q.strip().lower()
            target_vehicle = next(
                (v for v in all_vehicles if q_lower in v.registration_number.lower() or q_lower in v.vehicle_type.lower()),
                None,
            )

        if not target_vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found.")

        try:
            location = proxy.get_vehicle_location(target_vehicle.id)
            tracking_subject.receive_location_update(db, location)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))

        return LocationSearchResult(
            target_type="vehicle",
            target_id=target_vehicle.id,
            title=target_vehicle.registration_number,
            subtitle=f"{target_vehicle.vehicle_type} (Cap: {target_vehicle.capacity}kg)",
            is_assigned=True,
            vehicle_id=target_vehicle.id,
            registration_number=target_vehicle.registration_number,
            latitude=location.latitude,
            longitude=location.longitude,
            status=target_vehicle.status.value,
            message="Live vehicle GPS telemetry active.",
        )

    # Driver search
    driver_repo = DriverRepository(db)
    target_driver = None
    if id is not None:
        target_driver = driver_repo.get(id)
    elif q:
        all_drivers = driver_repo.list()
        q_lower = q.strip().lower()
        target_driver = next(
            (d for d in all_drivers if (d.user and q_lower in d.user.name.lower()) or q_lower in d.license_number.lower()),
            None,
        )

    if not target_driver:
        raise HTTPException(status_code=404, detail="Driver not found.")

    driver_name = target_driver.user.name if target_driver.user else f"Driver #{target_driver.id}"

    try:
        location = proxy.get_driver_location(target_driver.id)
        tracking_subject.receive_location_update(db, location)
        vehicle = VehicleRepository(db).get(location.vehicle_id) if location.vehicle_id else None

        return LocationSearchResult(
            target_type="driver",
            target_id=target_driver.id,
            title=driver_name,
            subtitle=f"License: {target_driver.license_number}",
            is_assigned=True,
            vehicle_id=location.vehicle_id,
            registration_number=vehicle.registration_number if vehicle else f"Vehicle #{location.vehicle_id}",
            latitude=location.latitude,
            longitude=location.longitude,
            status=target_driver.availability.value,
            message=f"Driver is assigned to vehicle {vehicle.registration_number if vehicle else location.vehicle_id}.",
        )
    except DriverNotAssignedError:
        return LocationSearchResult(
            target_type="driver",
            target_id=target_driver.id,
            title=driver_name,
            subtitle=f"License: {target_driver.license_number}",
            is_assigned=False,
            vehicle_id=None,
            registration_number=None,
            latitude=None,
            longitude=None,
            status=target_driver.availability.value,
            message="Driver is not assigned to any vehicle.",
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def submit_location_update(
    location_in: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept new live GPS coordinates for a vehicle, update adapter cache,
    record in LocationRepository, and broadcast to GPSTrackingSubject observers.
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user, db=db)

    # Validate authorization via proxy
    try:
        proxy.get_vehicle_location(location_in.vehicle_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    # Update adapter coordinate seed
    provider.set_coordinates(location_in.vehicle_id, location_in.latitude, location_in.longitude)

    ts_location = TrackSphereLocation(
        vehicle_id=location_in.vehicle_id,
        latitude=location_in.latitude,
        longitude=location_in.longitude,
        timestamp=location_in.timestamp or datetime.now(timezone.utc),
    )

    # Persist and notify observers
    saved_location = tracking_subject.receive_location_update(db, ts_location)

    return LocationRead(
        vehicle_id=saved_location.vehicle_id,
        latitude=saved_location.latitude,
        longitude=saved_location.longitude,
        timestamp=saved_location.timestamp,
    )


@router.get("/{vehicle_id}", response_model=LocationRead)
def get_vehicle_location(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch vehicle location using SimulatedGPSAdapter adapted via LocationProvider,
    processed by TrackSphereLocationService and protected by LocationServiceProxy (Protection Proxy Pattern).
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user, db=db)

    try:
        location = proxy.get_vehicle_location(vehicle_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    # Persist and notify observers via GPSTrackingSubject
    tracking_subject.receive_location_update(db, location)

    return LocationRead(
        vehicle_id=location.vehicle_id,
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=location.timestamp,
    )


@router.get("/{vehicle_id}/history", response_model=list[LocationRead])
def get_vehicle_location_history(
    vehicle_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve historical GPS breadcrumbs for a vehicle.
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user, db=db)

    try:
        # Check permissions via proxy first
        proxy.get_vehicle_location(vehicle_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    repo = LocationRepository(db)
    history = repo.get_history_by_vehicle(vehicle_id, limit=limit)
    return [
        LocationRead(
            vehicle_id=h.vehicle_id,
            latitude=h.latitude,
            longitude=h.longitude,
            timestamp=h.timestamp,
        )
        for h in history
    ]


class WebSocketConnectionManager(Observer):
    def __init__(self):
        self.active_queues: list[asyncio.Queue] = []
        self._loop = None

    def _get_loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
        return self._loop

    async def connect(self, websocket: WebSocket) -> asyncio.Queue:
        await websocket.accept()
        queue = asyncio.Queue()
        self.active_queues.append(queue)
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return queue

    def disconnect(self, queue: asyncio.Queue):
        if queue in self.active_queues:
            self.active_queues.remove(queue)

    def update(self, event_type: str, data: dict[str, Any]) -> None:
        """
        Synchronous update called by GPSTrackingSubject.
        Pushes to async queues safely across thread boundaries.
        """
        if event_type == "LOCATION_UPDATE":
            loop = self._get_loop()
            if loop and loop.is_running():
                for queue in self.active_queues:
                    loop.call_soon_threadsafe(queue.put_nowait, data)

ws_manager = WebSocketConnectionManager()
tracking_subject.attach(ws_manager)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time telemetry updates.
    Replaces client-side HTTP polling.
    """
    queue = await ws_manager.connect(websocket)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        ws_manager.disconnect(queue)
    except asyncio.CancelledError:
        ws_manager.disconnect(queue)

