# TrackSphere Architecture

## Overview

TrackSphere is a small fleet and delivery management application designed to demonstrate multiple Gang-of-Four design patterns within a coherent layered architecture.

## Layered Architecture

The initial structure follows a layered approach:

- `tracksphere/app/api/` - FastAPI route definitions and HTTP delivery.
- `tracksphere/app/application/` - application services, workflows, and facades.
- `tracksphere/app/domain/` - core domain concepts and business rules.
- `tracksphere/app/repositories/` - repository interfaces and persistence abstractions.
- `tracksphere/app/infrastructure/` - infrastructure code such as configuration, adapters, and database connectors.
- `tracksphere/app/models/` - SQLAlchemy models.
- `tracksphere/app/schemas/` - Pydantic schemas.
- `tracksphere/app/templates/` - server-rendered HTML templates.
- `tracksphere/app/static/` - static assets (CSS, JavaScript).

## Pattern Roadmap

### Strategy
Delivery assignment algorithms are encapsulated behind an `AssignmentStrategy` interface and used by `AssignmentService` to keep assignment workflows decoupled from strategy selection.

### Observer
Delivery events will notify observers such as notification dispatchers and dashboard refresh handlers.

### Singleton
A singleton will manage application-wide configuration and environment settings.

### Factory
A factory will create role-aware user/domain objects.

### Abstract Factory
Role-specific families of application components will be created by an abstract factory.

### Façade
A delivery management façade will simplify assignment and status workflows for route handlers.

### Adapter
Location simulation providers will be adapted into the internal location model using a `LocationProvider` interface and adapter classes.

### Composite
Delivery and package hierarchies will allow grouping of deliveries and sub-packages.

### Proxy
Access to sensitive location/location details will be protected through proxy objects using `LocationServiceProxy` for role-based access control.

### Decorator
Notifications will be dynamically enhanced with metadata such as priority, driver context, and formatting.

### Builder
Complex `Delivery` creation will be built step-by-step through a builder.

## Persistence Architecture

The application now includes a persistence foundation using SQLAlchemy and SQLite.

- `app/models/` defines SQLAlchemy ORM models for `User`, `Driver`, `Vehicle`, `Delivery`, `Assignment`, `Notification`, and `Location`.
- `app/infrastructure/database.py` provides the database engine, session factory, FastAPI dependency, and initialization logic.
- `app/infrastructure/config.py` implements the `ConfigurationManager` singleton for application-wide configuration.
- `app/infrastructure/seeds.py` adds deterministic development seed data.
- `app/repositories/` contains repository classes for core entities.
- `app/api/` exposes REST endpoints that use repository classes through dependency injection.

## Deviation Notes

The implementation remains aligned with the layered architecture. The only addition is a test-specific database reset fixture to support deterministic SQLite test isolation on Windows.
