from fastapi import APIRouter

from . import users, drivers, vehicles, deliveries, notifications, locations, auth, web

router = APIRouter()

router.include_router(auth.router)
router.include_router(web.router)
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
router.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])
router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
router.include_router(locations.router, prefix="/locations", tags=["locations"])
