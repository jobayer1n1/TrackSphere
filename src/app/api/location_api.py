from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.locations.location_models import TrackSphereLocation
from app.core.locations.location_proxy import LocationServiceProxy
from app.core.locations.location_service import TrackSphereLocationService
from app.core.locations.simulated_gps_adapter import SimulatedGPSAdapter
from app.core.tracking.service import tracking_subject
from app.models.user import User
from app.repositories.location_repository import LocationRepository
from app.schemas.location import LocationCreate, LocationRead

router = APIRouter(prefix="/api/locations", tags=["Location & GPS Telemetry"])


@router.get("/driver/me", response_model=LocationRead)
def get_my_driver_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve live telemetry for current driver (assigned vehicle or driver filler GPS location).
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user)

    try:
        location = proxy.get_driver_location()
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


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def submit_location_update(
    location_in: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept new live GPS coordinates for a vehicle or driver, update adapter cache,
    record in LocationRepository, and broadcast to GPSTrackingSubject observers.
    """
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user)

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
    proxy = LocationServiceProxy(service, current_user)

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
    proxy = LocationServiceProxy(service, current_user)

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

