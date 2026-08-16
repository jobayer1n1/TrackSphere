# Observer Pattern

## Problem

Delivery state changes may require multiple reactions: notifications, dashboards, audit logs, or UI refreshes. If delivery logic directly knows every consumer, it becomes tightly coupled and hard to extend.

## TrackSphere Use Case

In TrackSphere, assignment and delivery status changes should publish events without knowing who consumes them. The Observer pattern decouples delivery events from notification and dashboard consumers.

## Participants

- `Subject` / `DeliveryEventSource`: maintains a list of observers and notifies them when events occur.
- `Observer`: interface for objects that react to delivery events.
- `NotificationObserver`: creates persisted notifications using `NotificationRepository`.
- `DashboardObserver`: records events for application-level dashboards or monitoring.
- `DeliveryAssignedEvent`, `DeliveryStatusChangedEvent`, `DeliveryCompletedEvent`, `DeliveryCancelledEvent`: explicit event payloads.

## Event Flow

1. `AssignmentService` assigns a delivery.
2. `DeliveryEventSource.notify()` publishes a `DeliveryAssignedEvent`.
3. `NotificationObserver.update()` persists a notification.
4. `DashboardObserver.update()` stores the event for dashboard use.

## Coupling Before / After

Before:
- Delivery or assignment logic would instantiate notification services directly.
- Adding a new consumer required modifying the delivery workflow.

After:
- Workflow sends events to a subject.
- Observers can be added/removed without changing delivery logic.
- New consumers subscribe to events independently.

## Tests

- `tests/unit/test_observer.py`
  - attach/detach behavior
  - event propagation
  - multiple observers
  - notification persistence
- `tests/integration/test_assignment_observer_integration.py`
  - delivery assignment triggers a persisted notification
  - dashboard observer receives event

## Advantages

- Low coupling between event source and consumers.
- Easy extension with new observers.
- Clear event payloads separate transport from domain logic.

## Disadvantages

- Can be harder to trace control flow when many observers exist.
- Observers may need to manage their own persistence or state.
- Incorrect observer removal can cause stale subscriptions.
