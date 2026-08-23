from abc import ABC, abstractmethod
from typing import Any
from app.models.enums import UserRole


class User(ABC):
    """
    Abstract Base Class for Domain User entities (Inheritance Pattern).
    Defines common user behavior, identity attributes, and role permission hooks.
    """

    def __init__(self, user_id: int, name: str, email: str, role: UserRole, active: bool = True):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.active = active

    @abstractmethod
    def get_permissions(self) -> list[str]:
        """Return the list of permissions granted to this user role."""
        pass

    def has_permission(self, permission: str) -> bool:
        """Check if user possesses a specific permission string."""
        return permission in self.get_permissions()

    def update_profile(self, name: str | None = None, email: str | None = None) -> None:
        if name:
            self.name = name
        if email:
            self.email = email

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "active": self.active,
            "permissions": self.get_permissions(),
        }
