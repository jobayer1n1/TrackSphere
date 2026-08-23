from app.core.users.base import User
from app.models.enums import UserRole


class Dispatcher(User):
    """
    Dispatcher role entity.
    Manages delivery jobs, driver/vehicle assignments, transit monitoring, and dispatch alerts.
    """

    def __init__(self, user_id: int, name: str, email: str, active: bool = True):
        super().__init__(user_id, name, email, UserRole.DISPATCHER, active)

    def get_permissions(self) -> list[str]:
        return [
            "create_delivery",
            "update_delivery",
            "cancel_delivery",
            "assign_delivery",
            "reassign_delivery",
            "view_vehicles",
            "view_drivers",
            "view_all_telemetry",
            "send_dispatch_notifications",
        ]
