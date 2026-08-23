from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.facade.dashboard_facade import DashboardFacade
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Facade"])


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Facade Pattern Endpoint:
    Returns aggregated metrics tailored to the requesting user's role via DashboardFacade.
    """
    facade = DashboardFacade(db)

    if current_user.role == UserRole.ADMINISTRATOR:
        return facade.get_administrator_summary()
    elif current_user.role == UserRole.DISPATCHER:
        return facade.get_dispatcher_summary()
    else:
        return facade.get_driver_summary(current_user.id)
