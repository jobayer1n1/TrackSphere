# Builder Pattern

## Intent

Separate the construction of a complex object from its representation, enabling step-by-step creation.

## Problem

`Delivery` objects in TrackSphere require several fields, some of which are optional, and the construction should be readable and validated.

## TrackSphere Use Case

Delivery creation involves pickup, destination, deadline, priority, optional notes, optional assigned driver/vehicle, and optional package structure.
A builder makes this construction explicit and prevents invalid `Delivery` objects.

## Participants

- `DeliveryBuilder` — configures delivery fields step-by-step.
- `Delivery` — the resulting domain object persisted through SQLAlchemy.
- `DeliveryBuilderError` — raised when required fields are missing.

## Structure

- `app/domain/deliveries/delivery_builder.py`
- `app/models/__init__.py` (Delivery model)

## Runtime Flow

```python
from app.domain.deliveries.delivery_builder import DeliveryBuilder
from datetime import datetime

delivery = (
    DeliveryBuilder()
    .set_pickup("Warehouse A")
    .set_destination("Customer B")
    .set_deadline(datetime(2026, 12, 31, 18, 0, 0))
    .set_priority(1)
    .set_notes("Fragile")
    .build()
)
```

## Tests

- `tests/unit/test_builder_composite.py`

## Tradeoffs

Advantages:
- Clear, fluent construction.
- Validates required values before object creation.
- Keeps optional fields optional.

Disadvantages:
- Adds a dedicated construction class.
- Some complexity for a small domain object.

## Why This Is Genuine

This builder is used to create actual delivery domain objects and integrates with real delivery persistence and package aggregation logic.
