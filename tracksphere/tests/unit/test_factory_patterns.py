import pytest

from app.domain.users.role_component_factory import (
    AdministratorFactory,
    DispatcherFactory,
    DriverFactory,
    RoleComponentFactoryProducer,
)
from app.domain.users.user_factory import UserFactory, UserFactoryError
from app.models import UserRole


def test_user_factory_creates_administrator():
    user = UserFactory.create_user(
        name="Admin",
        email="admin@example.com",
        password_hash="secret",
        role=UserRole.ADMINISTRATOR,
    )

    assert user.role == UserRole.ADMINISTRATOR
    assert user.email == "admin@example.com"


def test_user_factory_creates_dispatcher():
    user = UserFactory.create_user(
        name="Dispatch",
        email="dispatch@example.com",
        password_hash="secret",
        role=UserRole.DISPATCHER,
    )

    assert user.role == UserRole.DISPATCHER
    assert user.name == "Dispatch"


def test_user_factory_creates_driver():
    user = UserFactory.create_user(
        name="Driver",
        email="driver@example.com",
        password_hash="secret",
        role=UserRole.DRIVER,
    )

    assert user.role == UserRole.DRIVER
    assert user.active is True


def test_user_factory_raises_for_invalid_role():
    with pytest.raises(UserFactoryError):
        UserFactory.create_user(
            name="Invalid",
            email="invalid@example.com",
            password_hash="secret",
            role="UNKNOWN",  # type: ignore[arg-type]
        )


def test_abstract_factory_administrator_family():
    factory = RoleComponentFactoryProducer.get_factory("ADMINISTRATOR")
    dashboard = factory.create_dashboard_configuration()
    permissions = factory.create_permission_set()
    menu = factory.create_navigation_menu()

    assert dashboard.title == "Administrator Dashboard"
    assert "manage_users" in permissions.permissions
    assert "Reports" in menu.items


def test_abstract_factory_dispatcher_family():
    factory = RoleComponentFactoryProducer.get_factory("DISPATCHER")
    dashboard = factory.create_dashboard_configuration()
    permissions = factory.create_permission_set()
    menu = factory.create_navigation_menu()

    assert dashboard.title == "Dispatcher Dashboard"
    assert "create_delivery" in permissions.permissions
    assert "Notifications" in menu.items


def test_abstract_factory_driver_family():
    factory = RoleComponentFactoryProducer.get_factory("DRIVER")
    dashboard = factory.create_dashboard_configuration()
    permissions = factory.create_permission_set()
    menu = factory.create_navigation_menu()

    assert dashboard.title == "Driver Dashboard"
    assert "update_status" in permissions.permissions
    assert "Vehicle Location" in menu.items


def test_abstract_factory_client_uses_abstraction():
    factory = RoleComponentFactoryProducer.get_factory("DRIVER")
    assert isinstance(factory, object)
    assert factory.create_dashboard_configuration().title == "Driver Dashboard"


def test_abstract_factory_can_be_substituted():
    admin_factory = AdministratorFactory()
    dispatcher_factory = DispatcherFactory()
    driver_factory = DriverFactory()

    assert admin_factory.create_permission_set().permissions != dispatcher_factory.create_permission_set().permissions
    assert dispatcher_factory.create_navigation_menu().items != driver_factory.create_navigation_menu().items
