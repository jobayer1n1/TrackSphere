# Adapter Pattern

## Intent

Convert the interface of an external service into one that the TrackSphere application can use.

## Problem

Location providers have differing output formats. TrackSphere must consume location data without depending on an external provider's representation.

## TrackSphere Use Case

Vehicle location data comes from an external or simulated provider.
The Adapter converts external location payloads into the internal `TrackSphereLocation` model.

## Participants

- `LocationProvider` - interface for fetching location data.
- `SimulatedGPSAdapter` - concrete adapter that converts simulated provider output to `TrackSphereLocation`.
- `TrackSphereLocation` - internal domain representation of location data.
- `TrackSphereLocationService` - service that uses a `LocationProvider`.

## Runtime Flow

1. `TrackSphereLocationService` asks a `LocationProvider` for vehicle location.
2. `SimulatedGPSAdapter` fetches simulated external data.
3. Adapter translates `lat`, `lon`, and `timestamp` into `TrackSphereLocation`.
4. Service returns the internal model to the application.

## Actual Classes

- `app.application.locations.location_provider.LocationProvider`
- `app.application.locations.location_models.TrackSphereLocation`
- `app.application.locations.simulated_gps_adapter.SimulatedGPSAdapter`
- `app.application.locations.location_service.TrackSphereLocationService`

## Tests

- `tests/unit/test_adapter_proxy.py`
  - verifies the adapter returns `TrackSphereLocation`
  - verifies location service uses the provider

## Tradeoffs

- Advantages: decouples TrackSphere from external data formats and lets providers vary independently.
- Disadvantages: adds a translation layer and a bit more complexity than using a single internal format only.

## Why this is genuinely the pattern

The adapter converts an incompatible external representation into the application's internal interface rather than directly exposing external provider details.
