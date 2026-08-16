# Composite Pattern

## Intent

Allow clients to treat individual objects and compositions of objects uniformly.

## Problem

Deliveries can include single packages or grouped collections of packages, and the system needs a common way to aggregate weight, volume, and item counts.

## TrackSphere Use Case

A delivery may contain a simple `Package` or a nested `PackageGroup` containing multiple packages and sub-groups. The composite enables uniform client interaction.

## Participants

- `DeliveryItem` — common component abstraction.
- `Package` — leaf object representing a single package.
- `PackageGroup` — composite object containing multiple `DeliveryItem` children.

## Structure

- `app/domain/deliveries/package_item.py`
- `app/domain/deliveries/delivery_builder.py`

## Runtime Flow

```python
from app.domain.deliveries.package_item import Package, PackageGroup

root = PackageGroup(name="Order 123")
root.add(Package(description="Box A", weight=5.0, volume=1.0))
root.add(Package(description="Box B", weight=10.0, volume=2.0))

subgroup = PackageGroup(name="Fragile Items")
subgroup.add(Package(description="Glassware", weight=2.5, volume=0.5))
root.add(subgroup)
```

## Tests

- `tests/unit/test_builder_composite.py`

## Tradeoffs

Advantages:
- Supports nested package hierarchies.
- Enables aggregated calculations across leaf and composite items.
- Hides tree traversal from client code.

Disadvantages:
- More abstraction and classes for package management.
- May be more than needed for simple deliveries.

## Why This Is Genuine

The composite is integrated into real delivery creation and description logic, and it supports nested package hierarchies for real TrackSphere delivery objects.
