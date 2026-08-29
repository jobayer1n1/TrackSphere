from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.core.auth.security import hash_password
from app.models.driver import Driver
from app.models.enums import UserRole
from app.models.user import User
from app.models.vehicle import Vehicle
from app.repositories.driver_repository import DriverRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter(prefix="/api", tags=["Users, Drivers & Vehicles"])


# --- Users Endpoints (Admin only) ---
@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMINISTRATOR])),
):
    return UserRepository(db).list()


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMINISTRATOR])),
):
    repo = UserRepository(db)
    if repo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        active=user_in.active,
    )
    return repo.create(new_user)


# --- Drivers Endpoints ---
@router.get("/drivers", response_model=list[DriverRead])
def list_drivers(
    db: Session = Depends(get_db),
    user: User = Depends(require_role([UserRole.ADMINISTRATOR, UserRole.DISPATCHER])),
):
    return DriverRepository(db).list()


@router.post("/drivers", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver_in: DriverCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMINISTRATOR])),
):
    driver_repo = DriverRepository(db)
    user_repo = UserRepository(db)

    user = user_repo.get(driver_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.role != UserRole.DRIVER:
        raise HTTPException(status_code=400, detail="Target user does not have DRIVER role.")
    if driver_repo.get_by_user_id(driver_in.user_id):
        raise HTTPException(status_code=400, detail="Driver profile already exists for this user.")
    if driver_repo.get_by_license(driver_in.license_number):
        raise HTTPException(status_code=400, detail="License number already in use.")

    new_driver = Driver(
        user_id=driver_in.user_id,
        license_number=driver_in.license_number,
        availability=driver_in.availability,
    )
    return driver_repo.create(new_driver)


# --- Vehicles Endpoints ---
@router.get("/vehicles", response_model=list[VehicleRead])
def list_vehicles(
    db: Session = Depends(get_db),
    user: User = Depends(require_role([UserRole.ADMINISTRATOR, UserRole.DISPATCHER])),
):
    return VehicleRepository(db).list()


@router.post("/vehicles", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMINISTRATOR])),
):
    repo = VehicleRepository(db)
    if repo.get_by_registration(vehicle_in.registration_number):
        raise HTTPException(status_code=400, detail="Registration number already registered.")

    new_vehicle = Vehicle(
        registration_number=vehicle_in.registration_number,
        vehicle_type=vehicle_in.vehicle_type,
        capacity=vehicle_in.capacity,
        status=vehicle_in.status,
    )
    return repo.create(new_vehicle)
