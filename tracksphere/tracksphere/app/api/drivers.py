from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..repositories.driver_repository import DriverRepository
from ..schemas import DriverRead

router = APIRouter()


@router.get("/", response_model=list[DriverRead])
def list_drivers(db: Session = Depends(get_db)):
    repository = DriverRepository(db)
    return repository.list()


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    repository = DriverRepository(db)
    driver = repository.get(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver
