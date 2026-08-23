from app.api.auth_api import router as auth_router
from app.api.user_api import router as user_router
from app.api.delivery_api import router as delivery_router
from app.api.location_api import router as location_router
from app.api.notification_api import router as notification_router
from app.api.dashboard_api import router as dashboard_router
from app.api.web_routes import router as web_router

__all__ = [
    "auth_router",
    "user_router",
    "delivery_router",
    "location_router",
    "notification_router",
    "dashboard_router",
    "web_router",
]
