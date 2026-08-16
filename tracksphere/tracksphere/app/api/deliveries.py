from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..application.facades.delivery_management_facade import DeliveryManagementFacade
from ..infrastructure.database import get_db
from ..models import DeliveryStatus
from ..repositories.assignments import AssignmentRepository
from ..repositories.delivery_repository import DeliveryRepository
from ..repositories.driver_repository import DriverRepository
from ..repositories.notification_repository import NotificationRepository
from ..schemas import DeliveryRead

router = APIRouter()


def _get_facade(db: Session) -> DeliveryManagementFacade:
    return DeliveryManagementFacade(
        delivery_repository=DeliveryRepository(db),
        assignment_repository=AssignmentRepository(db),
        notification_repository=NotificationRepository(db),
        driver_repository=DriverRepository(db),
    )


@router.get("/", response_model=list[DeliveryRead])
def list_deliveries(db: Session = Depends(get_db)):
    repository = DeliveryRepository(db)
    return repository.list()


@router.get("/{delivery_id}", response_model=DeliveryRead)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    repository = DeliveryRepository(db)
    delivery = repository.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.post("/", response_model=DeliveryRead)
def create_delivery(
    pickup: str,
    destination: str,
    deadline: datetime,
    priority: int,
    vehicle_id: int,
    driver_id: int | None = None,
    notes: str | None = None,
    db: Session = Depends(get_db),
):
    facade = _get_facade(db)
    delivery = facade.create_delivery(
        pickup=pickup,
        destination=destination,
        deadline=deadline,
        priority=priority,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        notes=notes,
    )
    return delivery


@router.post("/{delivery_id}/assign", response_model=DeliveryRead)
def assign_delivery(delivery_id: int, db: Session = Depends(get_db)):
    facade = _get_facade(db)
    delivery = facade.assign_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.patch("/{delivery_id}/status", response_model=DeliveryRead)
def update_delivery_status(delivery_id: int, status: DeliveryStatus, db: Session = Depends(get_db)):
    facade = _get_facade(db)
    delivery = facade.update_delivery_status(delivery_id, status)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.post("/{delivery_id}/cancel", response_model=DeliveryRead)
def cancel_delivery(delivery_id: int, db: Session = Depends(get_db)):
    facade = _get_facade(db)
    delivery = facade.cancel_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.get("/{delivery_id}/summary")
def get_delivery_summary(delivery_id: int, db: Session = Depends(get_db)):
    facade = _get_facade(db)
    summary = facade.get_delivery_summary(delivery_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return summary
