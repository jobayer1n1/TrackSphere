# Proxy Pattern

## Intent

Provide a surrogate or placeholder for another object to control access to it.

## Problem

Location data is sensitive and should not be accessible to all users without an access check.

## TrackSphere Use Case

TrackSphere exposes vehicle location data through a service, but the service should only be used by authorized roles.
A proxy enforces authorization before delegating to the actual `LocationService`.

## Participants

- `LocationServiceProxy` - controls access to the real location service.
- `TrackSphereLocationService` - the real service that fetches location through a provider.
- `LocationProvider` implementations - adapters that provide location data.
- `User` / `UserRole` - drive authorization decisions.

## Runtime Flow

1. API route constructs a `LocationServiceProxy` around `TrackSphereLocationService`.
2. The proxy checks the current user's role.
3. Administrators and dispatchers are allowed to fetch any vehicle location.
4. Drivers are allowed only for their own vehicle.
5. If denied, it raises a `PermissionError` and the API returns `403`.

## Actual Classes

- `app.application.locations.location_proxy.LocationServiceProxy`
- `app.application.locations.location_service.TrackSphereLocationService`
- `app.application.locations.simulated_gps_adapter.SimulatedGPSAdapter`

## Tests

- `tests/unit/test_adapter_proxy.py`
  - authorized admin access
  - authorized dispatcher access
  - denied driver access to other vehicles
  - denied access does not invoke the real service

## Tradeoffs

- Advantages: centralizes access control and keeps authorization out of route handlers.
- Disadvantages: proxies can add indirection and require careful role mapping.

## Why this is genuinely the pattern

The proxy provides a protective interface to the real service, enforcing access rules before delegation.
