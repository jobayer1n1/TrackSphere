from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.core.assignment.service import AssignmentService
from app.core.assignment.strategies import get_assignment_strategy
from app.core.notifications.service import NotificationService
from app.models.delivery import Delivery
from app.models.enums import AvailabilityStatus, DeliveryStatus, NotificationPriority, NotificationType, UserRole, VehicleStatus
from app.models.user import User
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.assignment import AssignmentCreate, AssignmentRead
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryRead,
    DeliveryStatusUpdate,
    DeliveryUpdate,
)

router = APIRouter(prefix="/api/deliveries", tags=["Deliveries & Assignments"])


@router.get("", response_model=list[DeliveryRead])
def list_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = DeliveryRepository(db)
    if current_user.role == UserRole.DRIVER:
        driver = DriverRepository(db).get_by_user_id(current_user.id)
        if not driver:
            return []
        return repo.list_by_driver(driver.id)
    return repo.list()


@router.get("/{delivery_id}", response_model=DeliveryRead)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = DeliveryRepository(db)
    delivery = repo.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found.")

    if current_user.role == UserRole.DRIVER:
        driver = DriverRepository(db).get_by_user_id(current_user.id)
        if not driver or delivery.driver_id != driver.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this delivery.")

    return delivery


@router.post("", response_model=DeliveryRead, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery_in: DeliveryCreate,
    db: Session = Depends(get_db),
    dispatcher: User = Depends(require_role([UserRole.ADMINISTRATOR, UserRole.DISPATCHER])),
):
    repo = DeliveryRepository(db)
    new_delivery = Delivery(
        pickup=delivery_in.pickup,
        destination=delivery_in.destination,
        deadline=delivery_in.deadline,
        priority=delivery_in.priority,
        status=DeliveryStatus.PENDING,
        notes=delivery_in.notes,
    )
    saved = repo.create(new_delivery)

    # If driver and vehicle provided, assign immediately with dynamic strategy
    if delivery_in.driver_id and delivery_in.vehicle_id:
        strategy = get_assignment_strategy(priority=delivery_in.priority)
        assign_svc = AssignmentService(strategy=strategy)
        assignment, msg = assign_svc.assign_delivery(
            db, saved.id, delivery_in.driver_id, delivery_in.vehicle_id
        )
        if not assignment:
            raise HTTPException(status_code=400, detail=msg)

    return repo.get(saved.id)


@router.post("/{delivery_id}/assign", response_model=AssignmentRead)
def assign_delivery(
    delivery_id: int,
    assign_in: AssignmentCreate,
    db: Session = Depends(get_db),
    dispatcher: User = Depends(require_role([UserRole.ADMINISTRATOR, UserRole.DISPATCHER])),
):
    if not assign_in.vehicle_id:
        raise HTTPException(status_code=400, detail="Vehicle ID is required for assignment.")

    delivery = DeliveryRepository(db).get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found.")

    # Strategy Pattern: Resolve strategy dynamically based on explicit request or delivery priority
    strategy = get_assignment_strategy(
        strategy_name=assign_in.strategy,
        priority=delivery.priority,
    )
    assign_svc = AssignmentService(strategy=strategy)
    assignment, msg = assign_svc.assign_delivery(
        db, delivery_id, assign_in.driver_id, assign_in.vehicle_id
    )
    if not assignment:
        raise HTTPException(status_code=400, detail=msg)

    # Send Notification to Driver
    driver = DriverRepository(db).get(assign_in.driver_id)
    if driver and driver.user_id:
        notif_svc = NotificationService.get_instance()
        notif_svc.notify(
            db=db,
            recipient_id=driver.user_id,
            raw_message=f"You have been assigned to Delivery #{delivery_id}.",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.HIGH,
        )

    return assignment


@router.patch("/{delivery_id}/status", response_model=DeliveryRead)
def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = DeliveryRepository(db)
    delivery = repo.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found.")

    if current_user.role == UserRole.DRIVER:
        driver = DriverRepository(db).get_by_user_id(current_user.id)
        if not driver or delivery.driver_id != driver.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this delivery.")

        # Driver can transition to IN_PROGRESS or COMPLETED
        if status_update.status not in [DeliveryStatus.IN_PROGRESS, DeliveryStatus.COMPLETED]:
            raise HTTPException(status_code=400, detail="Driver can only set status to IN_PROGRESS or COMPLETED.")

    new_status = status_update.status
    repo.update(delivery, status=new_status)

    # When delivery is COMPLETED, release driver & vehicle
    if new_status == DeliveryStatus.COMPLETED:
        if delivery.driver_id:
            DriverRepository(db).update(delivery.driver, availability=AvailabilityStatus.AVAILABLE)
        if delivery.vehicle_id:
            VehicleRepository(db).update(delivery.vehicle, status=VehicleStatus.AVAILABLE)

    return delivery
