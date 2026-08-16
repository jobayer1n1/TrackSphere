# Decorator Pattern

## Intent

Attach additional behavior to notifications dynamically without modifying their original implementation.

## Problem

TrackSphere notifications need extra metadata and formatting that vary by workflow, but the base notification should remain reusable.

## TrackSphere Use Case

A delivery assignment notification may need priority escalation, timestamp overrides, and logging annotations.
The Decorator pattern wraps a base notification to add these behaviors dynamically.

## Participants

- `BasicNotification` - the concrete component representing a notification.
- `NotificationDecorator` - abstract decorator that delegates notification behavior.
- `PriorityDecorator` - overrides priority dynamically.
- `TimestampDecorator` - adds or overrides timestamps.
- `LoggingDecorator` - annotates messages for downstream logging.

## Runtime Flow

1. `DeliveryManagementFacade` creates a `BasicNotification`.
2. It wraps the notification with `PriorityDecorator` and `TimestampDecorator`.
3. It optionally wraps the result with `LoggingDecorator`.
4. It calls `build()` to create the persisted `Notification` model.

## Actual Classes

- `app.application.notifications.notification_decorator.BasicNotification`
- `app.application.notifications.notification_decorator.NotificationDecorator`
- `app.application.notifications.notification_decorator.PriorityDecorator`
- `app.application.notifications.notification_decorator.TimestampDecorator`
- `app.application.notifications.notification_decorator.LoggingDecorator`
- `app.application.facades.delivery_management_facade.DeliveryManagementFacade`

## Tests

- `tests/unit/test_decorator_facade.py`
  - verifies `BasicNotification` build
  - verifies `PriorityDecorator` overrides priority
  - verifies `TimestampDecorator` changes timestamps
  - verifies decorators compose correctly
  - verifies original object remains usable

## Tradeoffs

- Advantages: adds flexible notification behavior without changing the notification model.
- Disadvantages: decorator stacks can become harder to trace if too many wrappers are used.

## Why this is genuinely the pattern

The decorator maintains the notification interface, wraps a core notification object, and adds metadata without changing the wrapped object.
