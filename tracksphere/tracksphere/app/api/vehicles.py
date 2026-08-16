from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..repositories.vehicle_repository import VehicleRepository
from ..schemas import VehicleRead

router = APIRouter()


@router.get("/", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    repository = VehicleRepository(db)
    return repository.list()


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    repository = VehicleRepository(db)
    vehicle = repository.get(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
