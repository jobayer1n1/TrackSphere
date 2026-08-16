from tracksphere.app.models import UserRole


class UserBase:
    def __init__(self, name: str, email: str, password_hash: str, active: bool = True):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.active = active

    @property
    def role(self) -> UserRole:
        raise NotImplementedError


class AdministratorUser(UserBase):
    @property
    def role(self) -> UserRole:
        return UserRole.ADMINISTRATOR


class DispatcherUser(UserBase):
    @property
    def role(self) -> UserRole:
        return UserRole.DISPATCHER


class DriverUser(UserBase):
    @property
    def role(self) -> UserRole:
        return UserRole.DRIVER
