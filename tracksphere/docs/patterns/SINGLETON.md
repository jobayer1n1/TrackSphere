# Singleton Pattern

## Problem

Some resources must be shared consistently across an application, such as configuration values loaded from environment variables.

## TrackSphere Use Case

`ConfigurationManager` provides a central, shared view of application configuration for database connection strings and environment settings.

## Participants

- `SingletonMeta`: metaclass that ensures only one instance of a singleton class exists.
- `ConfigurationManager`: singleton object that loads and exposes application configuration.

## Implementation

- The `SingletonMeta` metaclass stores a single instance per class.
- `ConfigurationManager` uses `SingletonMeta` so `ConfigurationManager()` always returns the same object.
- A `reset_instance()` helper exists for tests to isolate singleton state.

## Why it is appropriate

- Configuration is a genuinely application-wide resource.
- It is stable after startup and should be shared across layers.
- The singleton avoids repeated environment parsing and inconsistent config values.

## Review Notes

- Testability is preserved with `reset_instance()` for unit tests.
- Thread safety is strengthened by protecting instance creation with a `threading.Lock`.
- Hidden coupling is limited because only infrastructure and service setup depend on the singleton.

## Tests

- `tests/unit/test_singleton.py`
  - verifies that repeated construction returns the same instance.
  - verifies shared environment and database URL values.

## Advantages

- Provides a single source of truth for configuration.
- Avoids global module-level state spread across many files.
- Simplifies test isolation through explicit reset.

## Disadvantages

- Global state is still present and must be reset in tests.
- Not suitable for request-scoped or tenant-specific configuration.
- Can create hidden dependencies if used outside initialization code.
