from app.core.users.base import User
from app.models.enums import UserRole


class DriverUser(User):
    """
    Driver role entity.
    Restricted to viewing assigned deliveries, updating personal transit status, and accessing own vehicle telemetry.
    """

    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
        driver_id: int | None = None,
        license_number: str | None = None,
        active: bool = True,
    ):
        super().__init__(user_id, name, email, UserRole.DRIVER, active)
        self.driver_id = driver_id
        self.license_number = license_number

    def get_permissions(self) -> list[str]:
        return [
            "view_assigned_deliveries",
            "update_delivery_status",
            "view_assigned_vehicle_telemetry",
            "receive_notifications",
        ]
