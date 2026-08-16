# TrackSphere UML Overview

This document describes the key entry points, modules, and UML-style design relationships used by TrackSphere.

## Component Overview

- 	racksphere/main.py starts the FastAPI app, configures static files, and initializes the database.
- 	racksphere/app/api/ exposes HTTP endpoints for deliveries, locations, vehicles, drivers, users, notifications, and web pages.
- 	racksphere/app/application/ holds use-case services, strategy assignment logic, notification decorators, facade orchestration, and location adapters/proxies.
- 	racksphere/app/domain/ contains domain-level builders, factories, and role component creation logic.
- 	racksphere/app/repositories/ contains persistence abstractions for SQLAlchemy models.
- 	racksphere/app/infrastructure/ contains configuration, database setup, and deterministic seed data.
- 	racksphere/app/models/ declares ORM models for users, drivers, vehicles, deliveries, assignments, notifications, and locations.
- 	racksphere/app/schemas/ defines Pydantic response models used by FastAPI routes.

## UML-Style Flow: Location Request

1. Browser calls /locations/{vehicle_id} router in pp/api/locations.py.
2. The endpoint creates a SimulatedGPSAdapter and TrackSphereLocationService.
3. LocationServiceProxy wraps the service and checks the current user role.
4. If permitted, the proxy delegates to the service and returns a TrackSphereLocation.

## UML-Style Flow: Delivery Assignment

1. Client calls /deliveries/{id}/assign in pp/api/deliveries.py.
2. The endpoint uses DeliveryManagementFacade.
3. The facade delegates driver selection to AssignmentService, which uses an AssignmentStrategy.
4. The facade also creates notification objects and wraps them with decorators.

## Pattern Deployment

- Singleton: ConfigurationManager
- Factory: UserFactory
- Abstract Factory: RoleComponentFactory
- Builder: DeliveryBuilder
- Strategy: AssignmentStrategy and concrete assignment algorithms
- Observer: DeliveryEventSource with NotificationObserver and DashboardObserver
- Facade: DeliveryManagementFacade
- Adapter: SimulatedGPSAdapter
- Proxy: LocationServiceProxy
- Composite: DeliveryItem and package group trees
- Decorator: NotificationDecorator wrappers
