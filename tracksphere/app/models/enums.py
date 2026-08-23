import enum


class UserRole(str, enum.Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    DISPATCHER = "DISPATCHER"
    DRIVER = "DRIVER"


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class VehicleStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    MAINTENANCE = "MAINTENANCE"


class DeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class NotificationType(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"


class NotificationPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DeliveryPriority(int, enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
