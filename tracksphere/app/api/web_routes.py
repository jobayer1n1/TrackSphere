from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, get_db
from app.config import settings
from app.core.facade.dashboard_facade import DashboardFacade
from app.models.enums import DeliveryStatus, UserRole
from app.models.user import User
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vehicle_repository import VehicleRepository

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)


def _require_login(request: Request, db: Session) -> User | RedirectResponse:
    user = get_current_user_optional(request, None, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    return user


@router.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, None, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/logout")
def logout_page(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME)
    return response


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user

    facade = DashboardFacade(db)
    if user.role == UserRole.ADMINISTRATOR:
        summary = facade.get_administrator_summary()
    elif user.role == UserRole.DISPATCHER:
        summary = facade.get_dispatcher_summary()
    else:
        summary = facade.get_driver_summary(user.id)

    notifications = NotificationRepository(db).list_by_user(user.id)
    unread_count = sum(1 for n in notifications if not n.read)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "summary": summary,
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@router.get("/vehicle-locations", response_class=HTMLResponse)
def vehicle_locations(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user

    driver_repo = DriverRepository(db)
    vehicle_repo = VehicleRepository(db)
    delivery_repo = DeliveryRepository(db)

    is_driver = user.role == UserRole.DRIVER
    drivers = []
    vehicles = []
    assigned_vehicle = None

    if is_driver:
        driver = driver_repo.get_by_user_id(user.id)
        if driver:
            drivers = [driver]
            assigned_deliveries = delivery_repo.list_by_driver(driver.id)
            active_delivery = next(
                (d for d in assigned_deliveries if d.status in [DeliveryStatus.IN_PROGRESS, DeliveryStatus.ASSIGNED] and d.vehicle),
                None,
            )
            if active_delivery and active_delivery.vehicle:
                vehicles = [active_delivery.vehicle]
                assigned_vehicle = active_delivery.vehicle
    else:
        vehicles = vehicle_repo.list()
        drivers = driver_repo.list()

    return templates.TemplateResponse(
        "vehicle_locations.html",
        {
            "request": request,
            "user": user,
            "vehicles": vehicles,
            "drivers": drivers,
            "is_driver": is_driver,
            "assigned_vehicle": assigned_vehicle,
        },
    )




@router.get("/deliveries", response_class=HTMLResponse)
def deliveries_page(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user

    delivery_repo = DeliveryRepository(db)
    driver_repo = DriverRepository(db)
    vehicle_repo = VehicleRepository(db)

    if user.role == UserRole.DRIVER:
        driver = driver_repo.get_by_user_id(user.id)
        deliveries = delivery_repo.list_by_driver(driver.id) if driver else []
    else:
        deliveries = delivery_repo.list()

    drivers = driver_repo.list()
    vehicles = vehicle_repo.list()

    return templates.TemplateResponse(
        "deliveries.html",
        {
            "request": request,
            "user": user,
            "deliveries": deliveries,
            "drivers": drivers,
            "vehicles": vehicles,
        },
    )


@router.get("/vehicles", response_class=HTMLResponse)
def vehicles_page(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user

    vehicles = VehicleRepository(db).list()
    return templates.TemplateResponse(
        "vehicles.html",
        {
            "request": request,
            "user": user,
            "vehicles": vehicles,
        },
    )


@router.get("/drivers", response_class=HTMLResponse)
def drivers_page(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user

    drivers = DriverRepository(db).list()
    return templates.TemplateResponse(
        "drivers.html",
        {
            "request": request,
            "user": user,
            "drivers": drivers,
        },
    )


@router.get("/notifications", response_class=HTMLResponse)
def notifications_page(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user

    notifications = NotificationRepository(db).list_by_user(user.id)
    return templates.TemplateResponse(
        "notifications.html",
        {
            "request": request,
            "user": user,
            "notifications": notifications,
        },
    )
