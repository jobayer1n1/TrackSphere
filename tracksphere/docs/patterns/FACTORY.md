# Factory Pattern

## Intent

Create objects without exposing the instantiation logic to the client.

## Problem

TrackSphere needs a central way to create user objects for different roles without scattering role-specific construction details across the codebase.

## TrackSphere Use Case

User account creation is role-driven. Administrator, Dispatcher, and Driver users have distinct role values, and the creation logic should be centralized.

## Participants

- `UserFactory` — the factory that creates `User` objects.
- `UserRole` — the role enum that determines which concrete domain user to instantiate.
- `AdministratorUser`, `DispatcherUser`, `DriverUser` — concrete role-aware domain classes.
- `app.models.User` — the SQLAlchemy model built from the role-aware object.

## Class Relationships

- `UserFactory` depends on `UserRole`.
- `UserFactory` creates a role-specific domain user.
- The domain user provides its role and construction details to the `User` model.

## Runtime Example

```python
from app.domain.users.user_factory import UserFactory
from app.models import UserRole

user = UserFactory.create_user(
    name="Driver",
    email="driver@example.com",
    password_hash="hashed_password",
    role=UserRole.DRIVER,
)
```

## File Paths

- `tracksphere/app/domain/users/user_factory.py`
- `tracksphere/app/domain/users/entities.py`
- `tracksphere/app/models/__init__.py`

## Tests

- `tests/unit/test_factory_patterns.py`

## Advantages

- Centralizes user creation logic.
- Validates user roles in one place.
- Makes client code simpler and less coupled to concrete classes.

## Disadvantages

- Adds indirection.
- Requires additional classes for concrete domain users.

## Why This Is Genuine

This pattern is used for actual user creation logic, not just a toy example. The factory avoids exposing role-specific instantiation details to callers.
