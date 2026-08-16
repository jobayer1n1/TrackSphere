from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import get_current_user
from ..application.locations import (
    LocationServiceProxy,
    SimulatedGPSAdapter,
    TrackSphereLocationService,
)
from ..infrastructure.database import get_db
from ..models import Location, Vehicle, VehicleStatus
from ..repositories.vehicle_repository import VehicleRepository
from ..schemas import LocationRead, LocationUpdatePayload

router = APIRouter()


@router.get("/all_vehicles", response_model=list[LocationRead])
def get_all_vehicle_locations(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    repository = VehicleRepository(db)
    vehicles = repository.list()

    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user)

    try:
        locations = proxy.get_all_vehicle_locations(vehicles)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    result = []
    for loc in locations:
        vid = loc.vehicle_id
        db_loc = db.scalars(select(Location).where(Location.vehicle_id == vid)).first()
        if db_loc:
            result.append(LocationRead(
                vehicle_id=vid,
                latitude=db_loc.latitude,
                longitude=db_loc.longitude,
                timestamp=db_loc.timestamp
            ))
        else:
            result.append(LocationRead(**loc.__dict__))

    return result


@router.post("/update/{vehicle_id}", response_model=LocationRead)
@router.put("/update/{vehicle_id}", response_model=LocationRead)
def update_vehicle_location(
    vehicle_id: str,
    payload: LocationUpdatePayload,
    db: Session = Depends(get_db),
):
    target_ref = vehicle_id or payload.vehicle_id
    if not target_ref and payload.vehicle_id:
        target_ref = payload.vehicle_id

    target_str = str(target_ref) if target_ref is not None else ""

    vehicle = None
    if target_str.isdigit():
        vehicle = db.get(Vehicle, int(target_str))

    if not vehicle and target_str:
        vehicle = db.scalars(select(Vehicle).where(Vehicle.registration_number == target_str)).first()

    if not vehicle and payload.vehicle_id:
        p_str = str(payload.vehicle_id)
        if p_str.isdigit():
            vehicle = db.get(Vehicle, int(p_str))
        if not vehicle:
            vehicle = db.scalars(select(Vehicle).where(Vehicle.registration_number == p_str)).first()

    if not vehicle:
        reg_num = target_str or str(payload.vehicle_id or "BUS-001")
        vehicle = Vehicle(
            registration_number=reg_num,
            vehicle_type="Bus" if "BUS" in reg_num.upper() else "Vehicle",
            capacity=1000,
            status=VehicleStatus.AVAILABLE,
        )
        db.add(vehicle)
        db.flush()

    parsed_timestamp = datetime.utcnow()
    if payload.timestamp:
        if isinstance(payload.timestamp, datetime):
            parsed_timestamp = payload.timestamp
        elif isinstance(payload.timestamp, str):
            try:
                parsed_timestamp = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
            except ValueError:
                parsed_timestamp = datetime.utcnow()

    location = db.scalars(select(Location).where(Location.vehicle_id == vehicle.id)).first()
    if location:
        location.latitude = payload.latitude
        location.longitude = payload.longitude
        location.timestamp = parsed_timestamp
    else:
        location = Location(
            vehicle_id=vehicle.id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timestamp=parsed_timestamp,
        )
        db.add(location)

    db.commit()
    db.refresh(location)

    # Sync into SimulatedGPSAdapter seed so realtime views immediately show the update
    if hasattr(SimulatedGPSAdapter, "_seed"):
        SimulatedGPSAdapter._seed[vehicle.id] = (payload.latitude, payload.longitude)

    return LocationRead(
        vehicle_id=vehicle.id,
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=location.timestamp,
    )


@router.get("/{vehicle_id}", response_model=LocationRead)
def get_vehicle_location(vehicle_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, current_user)

    try:
        location = proxy.get_vehicle_location(vehicle_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    db_loc = db.scalars(select(Location).where(Location.vehicle_id == vehicle_id)).first()
    if db_loc:
        return LocationRead(
            vehicle_id=vehicle_id,
            latitude=db_loc.latitude,
            longitude=db_loc.longitude,
            timestamp=db_loc.timestamp
        )

    return LocationRead(**location.__dict__)



