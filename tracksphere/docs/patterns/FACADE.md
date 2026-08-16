# Façade Pattern

## Intent

Provide a simplified interface to a set of complex subsystem workflows.

## Problem

FastAPI endpoints should not orchestrate multiple services, strategy selection, event generation, and notification creation directly.

## TrackSphere Use Case

A `DeliveryManagementFacade` coordinates delivery creation, assignment, status updates, and cancellations across repositories, strategy-based assignment, and notification decorators.

## Participants

- `DeliveryManagementFacade` - simplified workflow interface.
- `AssignmentService` - handles assignment strategy and event notification.
- `DeliveryEventSource` / Observer - notifies observers when delivery events occur.
- `DeliveryRepository`, `AssignmentRepository`, `NotificationRepository`, `DriverRepository` - persistence subsystems.

## Runtime Flow

1. FastAPI route calls `DeliveryManagementFacade`.
2. The facade creates or updates a delivery.
3. It delegates assignment to `AssignmentService`.
4. It notifies observers and creates decorated notifications.

## Actual Classes

- `app.application.facades.delivery_management_facade.DeliveryManagementFacade`
- `app.application.assignments.assignment_service.AssignmentService`
- `app.application.notifications.subject.DeliveryEventSource`
- `app.application.notifications.notification_decorator.BasicNotification`
- `app.application.notifications.notification_decorator.PriorityDecorator`
- `app.application.notifications.notification_decorator.TimestampDecorator`

## Tests

- `tests/unit/test_decorator_facade.py`
  - create workflow
  - assignment workflow
  - status update
  - cancellation
  - notification integration

## Tradeoffs

- Advantages: reduces API route complexity and centralizes workflow coordination.
- Disadvantages: the facade must remain a coordinator and not absorb business rules.

## Why this is genuinely the pattern

The facade hides subsystems behind a single entry point and delegates work to assignment, repository, and notification subsystems.
