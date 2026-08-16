# Abstract Factory Pattern

## Intent

Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

## Problem

TrackSphere needs role-specific UI component families for different user roles, but the client code should not refer to concrete role implementations directly.

## TrackSphere Use Case

Each role in TrackSphere has a specific dashboard configuration, permission set, and navigation menu.
The abstract factory allows the application to obtain a consistent family of role-specific components.

## Participants

- `RoleComponentFactory` — abstract factory interface.
- `AdministratorFactory`, `DispatcherFactory`, `DriverFactory` — concrete factories.
- `DashboardConfiguration`, `PermissionSet`, `NavigationMenu` — component products.
- `RoleComponentFactoryProducer` — factory producer that returns the correct concrete factory based on role.

## Class Relationships

- Client code requests a `RoleComponentFactory` from `RoleComponentFactoryProducer`.
- The concrete factory creates a family of related objects for that role.
- The client consumes `DashboardConfiguration`, `PermissionSet`, and `NavigationMenu` without knowing concrete classes.

## Runtime Example

```python
from app.domain.users.role_component_factory import RoleComponentFactoryProducer

factory = RoleComponentFactoryProducer.get_factory("DISPATCHER")
dashboard = factory.create_dashboard_configuration()
permissions = factory.create_permission_set()
menu = factory.create_navigation_menu()
```

## File Paths

- `tracksphere/app/domain/users/role_component_factory.py`

## Tests

- `tests/unit/test_factory_patterns.py`

## Advantages

- Keeps related role-specific component creation together.
- Makes code more extensible when adding new roles.
- Hides concrete object classes from the client.

## Disadvantages

- Adds extra layers and classes.
- Can be overkill for small applications.

## Why This Is Genuine

This pattern creates a family of related role-specific objects used by the application’s UI and permission logic, not a standalone demonstration.
