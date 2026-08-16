from app.models import User, UserRole, Driver, AvailabilityStatus, Vehicle, VehicleStatus, Delivery, DeliveryStatus, Notification, NotificationType, NotificationPriority, Location


def test_model_enums():
    assert UserRole.ADMINISTRATOR.value == "ADMINISTRATOR"
    assert AvailabilityStatus.AVAILABLE.value == "AVAILABLE"
    assert VehicleStatus.MAINTENANCE.value == "MAINTENANCE"
    assert DeliveryStatus.COMPLETED.value == "COMPLETED"
    assert NotificationType.ALERT.value == "ALERT"
    assert NotificationPriority.HIGH.value == "HIGH"


def test_relationship_types():
    assert issubclass(Driver, object)
    assert issubclass(Delivery, object)
    assert issubclass(Notification, object)
    assert issubclass(Location, object)
