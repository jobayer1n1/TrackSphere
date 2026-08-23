from app.core.users.administrator import Administrator
from app.core.users.base import User
from app.core.users.dispatcher import Dispatcher
from app.core.users.driver_user import DriverUser
from app.models.enums import UserRole


class UserFactory:
    """
    Factory Method Pattern:
    Dynamically instantiates concrete User subclass instances based on the requested UserRole.
    """

    @staticmethod
    def create_user(
        role: UserRole | str,
        user_id: int,
        name: str,
        email: str,
        active: bool = True,
        **kwargs,
    ) -> User:
        if isinstance(role, str):
            try:
                role = UserRole(role)
            except ValueError:
                raise ValueError(f"Invalid user role: {role}")

        if role == UserRole.ADMINISTRATOR:
            return Administrator(user_id=user_id, name=name, email=email, active=active)
        elif role == UserRole.DISPATCHER:
            return Dispatcher(user_id=user_id, name=name, email=email, active=active)
        elif role == UserRole.DRIVER:
            return DriverUser(
                user_id=user_id,
                name=name,
                email=email,
                driver_id=kwargs.get("driver_id"),
                license_number=kwargs.get("license_number"),
                active=active,
            )
        else:
            raise ValueError(f"Unsupported role for user factory: {role}")
