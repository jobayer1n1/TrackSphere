from app.core.users.base import User
from app.models.enums import UserRole


class Administrator(User):
    """
    Administrator role entity.
    Has full read/write privileges across users, vehicles, drivers, deliveries, and telemetry.
    """

    def __init__(self, user_id: int, name: str, email: str, active: bool = True):
        super().__init__(user_id, name, email, UserRole.ADMINISTRATOR, active)

    def get_permissions(self) -> list[str]:
        return [
            "manage_users",
            "manage_vehicles",
            "manage_drivers",
            "manage_deliveries",
            "assign_deliveries",
            "view_all_telemetry",
            "view_global_reports",
            "send_system_broadcasts",
        ]
