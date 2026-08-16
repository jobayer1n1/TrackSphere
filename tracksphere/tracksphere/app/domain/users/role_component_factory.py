from abc import ABC, abstractmethod


class DashboardConfiguration:
    def __init__(self, widgets: list[str], title: str):
        self.widgets = widgets
        self.title = title


class PermissionSet:
    def __init__(self, permissions: list[str]):
        self.permissions = permissions


class NavigationMenu:
    def __init__(self, items: list[str]):
        self.items = items


class RoleComponentFactory(ABC):
    @abstractmethod
    def create_dashboard_configuration(self) -> DashboardConfiguration:
        raise NotImplementedError

    @abstractmethod
    def create_permission_set(self) -> PermissionSet:
        raise NotImplementedError

    @abstractmethod
    def create_navigation_menu(self) -> NavigationMenu:
        raise NotImplementedError


class AdministratorFactory(RoleComponentFactory):
    def create_dashboard_configuration(self) -> DashboardConfiguration:
        return DashboardConfiguration(
            widgets=["system_summary", "user_activity", "vehicle_status"],
            title="Administrator Dashboard",
        )

    def create_permission_set(self) -> PermissionSet:
        return PermissionSet(
            permissions=["manage_users", "manage_drivers", "manage_vehicles", "view_reports"],
        )

    def create_navigation_menu(self) -> NavigationMenu:
        return NavigationMenu(
            items=["Dashboard", "Users", "Drivers", "Vehicles", "Deliveries", "Reports"],
        )


class DispatcherFactory(RoleComponentFactory):
    def create_dashboard_configuration(self) -> DashboardConfiguration:
        return DashboardConfiguration(
            widgets=["delivery_queue", "driver_status", "vehicle_availability"],
            title="Dispatcher Dashboard",
        )

    def create_permission_set(self) -> PermissionSet:
        return PermissionSet(
            permissions=["create_delivery", "assign_delivery", "monitor_status"],
        )

    def create_navigation_menu(self) -> NavigationMenu:
        return NavigationMenu(
            items=["Dashboard", "Deliveries", "Drivers", "Vehicles", "Notifications"],
        )


class DriverFactory(RoleComponentFactory):
    def create_dashboard_configuration(self) -> DashboardConfiguration:
        return DashboardConfiguration(
            widgets=["assigned_deliveries", "route_preview", "vehicle_status"],
            title="Driver Dashboard",
        )

    def create_permission_set(self) -> PermissionSet:
        return PermissionSet(
            permissions=["view_assignments", "update_status", "view_notifications"],
        )

    def create_navigation_menu(self) -> NavigationMenu:
        return NavigationMenu(
            items=["My Deliveries", "Notifications", "Vehicle Location"],
        )


class RoleComponentFactoryProducer:
    @staticmethod
    def get_factory(role: str) -> RoleComponentFactory:
        if role == "ADMINISTRATOR":
            return AdministratorFactory()
        if role == "DISPATCHER":
            return DispatcherFactory()
        if role == "DRIVER":
            return DriverFactory()
        raise ValueError(f"Unsupported role for component factory: {role}")
