from datetime import datetime

import pytest

from app.application.locations import (
    LocationServiceProxy,
    SimulatedGPSAdapter,
    TrackSphereLocationService,
    TrackSphereLocation,
)
from app.models import User, UserRole, Driver


def test_simulated_gps_adapter_translates_external_format():
    adapter = SimulatedGPSAdapter()
    location = adapter.fetch_location(1)

    assert isinstance(location, TrackSphereLocation)
    assert location.vehicle_id == 1
    assert location.latitude == 40.7128
    assert location.longitude == -74.0060
    assert isinstance(location.timestamp, datetime)


def test_location_service_returns_location_from_provider():
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    location = service.get_vehicle_location(2)

    assert location.vehicle_id == 2
    assert location.latitude == 34.0522


def test_proxy_allows_administrator():
    admin = User(id=1, name="Admin", email="admin@example.com", password_hash="pw", role=UserRole.ADMINISTRATOR, active=True)
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, admin)

    location = proxy.get_vehicle_location(1)
    assert location.vehicle_id == 1


def test_proxy_allows_dispatcher():
    dispatcher = User(id=2, name="Dispatch", email="dispatch@example.com", password_hash="pw", role=UserRole.DISPATCHER, active=True)
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, dispatcher)

    location = proxy.get_vehicle_location(3)
    assert location.vehicle_id == 3


def test_proxy_denies_driver_for_other_vehicle():
    driver_user = User(id=3, name="Driver", email="driver@example.com", password_hash="pw", role=UserRole.DRIVER, active=True)
    dummy_driver = Driver(id=1, user_id=3, license_number="LIC-1", availability="AVAILABLE")
    driver_user.driver = dummy_driver

    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, driver_user)

    with pytest.raises(PermissionError):
        proxy.get_vehicle_location(2)


def test_proxy_denied_driver_does_not_invoke_real_service():
    class FakeLocationService:
        def get_vehicle_location(self, vehicle_id: int):
            raise AssertionError("Real service should not be invoked for unauthorized access")

    driver_user = User(id=3, name="Driver", email="driver@example.com", password_hash="pw", role=UserRole.DRIVER, active=True)
    dummy_driver = Driver(id=1, user_id=3, license_number="LIC-1", availability="AVAILABLE")
    driver_user.driver = dummy_driver

    service = FakeLocationService()
    proxy = LocationServiceProxy(service, driver_user)

    with pytest.raises(PermissionError):
        proxy.get_vehicle_location(2)


def test_proxy_allows_driver_for_own_vehicle():
    driver_user = User(id=4, name="Driver2", email="driver2@example.com", password_hash="pw", role=UserRole.DRIVER, active=True)
    dummy_driver = Driver(id=4, user_id=4, license_number="LIC-4", availability="AVAILABLE")
    driver_user.driver = dummy_driver

    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, driver_user)

    location = proxy.get_vehicle_location(4)
    assert location.vehicle_id == 4


def test_proxy_get_all_vehicles_administrator():
    admin = User(id=1, name="Admin", email="admin@example.com", password_hash="pw", role=UserRole.ADMINISTRATOR, active=True)
    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, admin)

    locations = proxy.get_all_vehicle_locations([1, 2, 3])
    assert len(locations) == 3
    assert [loc.vehicle_id for loc in locations] == [1, 2, 3]


def test_proxy_get_all_vehicles_driver_filters_accessible():
    driver_user = User(id=4, name="Driver2", email="driver2@example.com", password_hash="pw", role=UserRole.DRIVER, active=True)
    dummy_driver = Driver(id=1, user_id=4, license_number="LIC-4", availability="AVAILABLE")
    driver_user.driver = dummy_driver

    provider = SimulatedGPSAdapter()
    service = TrackSphereLocationService(provider)
    proxy = LocationServiceProxy(service, driver_user)

    # Driver 1 has access to vehicle 1, but not vehicles 2 or 3
    locations = proxy.get_all_vehicle_locations([1, 2, 3])
    assert len(locations) == 1
    assert locations[0].vehicle_id == 1

