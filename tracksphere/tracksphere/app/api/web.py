from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..application.auth import verify_session_token
from ..infrastructure.database import get_db
from ..repositories.delivery_repository import DeliveryRepository
from ..repositories.driver_repository import DriverRepository
from ..repositories.notification_repository import NotificationRepository
from ..repositories.user_repository import UserRepository
from ..repositories.vehicle_repository import VehicleRepository

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("tracksphere_session")
    if token is None:
        return None
    user_id = verify_session_token(token)
    if user_id is None:
        return None
    return UserRepository(db).get(user_id)


def _require_login(request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    return user


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user
    deliveries = DeliveryRepository(db).list()
    drivers = DriverRepository(db).list()
    vehicles = VehicleRepository(db).list()
    notifications = NotificationRepository(db).list()
    users = UserRepository(db).list()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "deliveries": deliveries,
            "drivers": drivers,
            "vehicles": vehicles,
            "notifications": notifications,
            "users": users,
        },
    )


@router.get("/vehicle-locations", response_class=HTMLResponse)
def vehicle_locations(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user
    vehicles = VehicleRepository(db).list()
    return templates.TemplateResponse(
        "vehicle_locations.html",
        {
            "request": request,
            "user": user,
            "vehicles": vehicles,
        },
    )


@router.get("/notifications", response_class=HTMLResponse)
def notifications(request: Request, db: Session = Depends(get_db)):
    user = _require_login(request, db)
    if isinstance(user, RedirectResponse):
        return user
    notifications = NotificationRepository(db).list()
    return templates.TemplateResponse(
        "notifications.html", {"request": request, "user": user, "notifications": notifications})
