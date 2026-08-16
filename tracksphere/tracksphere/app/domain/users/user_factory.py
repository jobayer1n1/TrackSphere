from tracksphere.app.models import User, UserRole
from tracksphere.app.domain.users.entities import AdministratorUser, DispatcherUser, DriverUser


class UserFactoryError(ValueError):
    pass


class UserFactory:
    @staticmethod
    def create_user(
        name: str,
        email: str,
        password_hash: str,
        role: UserRole,
        active: bool = True,
    ) -> User:
        if role == UserRole.ADMINISTRATOR:
            domain_user = AdministratorUser(name, email, password_hash, active)
        elif role == UserRole.DISPATCHER:
            domain_user = DispatcherUser(name, email, password_hash, active)
        elif role == UserRole.DRIVER:
            domain_user = DriverUser(name, email, password_hash, active)
        else:
            raise UserFactoryError(f"Unsupported user role: {role}")

        return User(
            name=domain_user.name,
            email=domain_user.email,
            password_hash=domain_user.password_hash,
            role=domain_user.role,
            active=domain_user.active,
        )
