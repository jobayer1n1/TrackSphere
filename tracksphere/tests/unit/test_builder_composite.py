from datetime import datetime

from app.domain.deliveries.delivery_builder import DeliveryBuilder, DeliveryBuilderError
from app.domain.deliveries.package_item import Package, PackageGroup


def test_delivery_builder_valid_delivery():
    delivery = (
        DeliveryBuilder()
        .set_pickup("Warehouse A")
        .set_destination("Customer B")
        .set_deadline(datetime(2026, 12, 31, 18, 0, 0))
        .set_priority(1)
        .set_notes("Handle with care")
        .build()
    )

    assert delivery.pickup == "Warehouse A"
    assert delivery.destination == "Customer B"
    assert delivery.notes == "Handle with care"
    assert delivery.status.name == "PENDING"


def test_delivery_builder_missing_required_fields():
    builder = DeliveryBuilder().set_pickup("Warehouse A")
    try:
        builder.build()
        assert False, "Expected DeliveryBuilderError"
    except DeliveryBuilderError as exc:
        assert "destination" in str(exc) or "deadline" in str(exc) or "priority" in str(exc)


def test_delivery_builder_optional_fields():
    delivery = (
        DeliveryBuilder()
        .set_pickup("Warehouse A")
        .set_destination("Customer B")
        .set_deadline(datetime(2026, 12, 31, 18, 0, 0))
        .set_priority(2)
        .set_driver(1)
        .set_vehicle(1)
        .build()
    )

    assert delivery.driver_id == 1
    assert delivery.vehicle_id == 1
    assert delivery.priority == 2


def test_composite_leaf_package():
    package = Package(description="Box 1", weight=10.0, volume=2.5)
    assert package.get_total_weight() == 10.0
    assert package.get_total_volume() == 2.5
    assert package.get_item_count() == 1
    assert "Box 1" in package.describe()


def test_composite_group_aggregation():
    group = PackageGroup(name="Group 1")
    group.add(Package(description="Box 1", weight=5.0, volume=1.0))
    group.add(Package(description="Box 2", weight=15.0, volume=3.0))

    assert group.get_total_weight() == 20.0
    assert group.get_total_volume() == 4.0
    assert group.get_item_count() == 2
    assert "PackageGroup(name=Group 1" in group.describe()


def test_composite_nested_group():
    root = PackageGroup(name="Root")
    child = PackageGroup(name="Child")
    child.add(Package(description="Box 1", weight=5.0, volume=1.0))
    child.add(Package(description="Box 2", weight=2.0, volume=0.5))
    root.add(child)
    root.add(Package(description="Box 3", weight=3.0, volume=0.8))

    assert root.get_total_weight() == 10.0
    assert root.get_total_volume() == 2.3
    assert root.get_item_count() == 3
    assert "Root" in root.describe()


def test_builder_composite_integration():
    group = PackageGroup(name="Delivery Packages")
    group.add(Package(description="Box A", weight=10.0, volume=2.0))
    group.add(Package(description="Box B", weight=20.0, volume=4.5))

    delivery = (
        DeliveryBuilder()
        .set_pickup("Warehouse A")
        .set_destination("Customer B")
        .set_deadline(datetime(2026, 12, 31, 18, 0, 0))
        .set_priority(1)
        .set_notes("Contains packages")
        .set_package_group(group)
        .build()
    )

    assert "Package summary" in delivery.notes
    assert "Box A" in delivery.notes
    assert delivery.driver_id is None
    assert delivery.vehicle_id is None
