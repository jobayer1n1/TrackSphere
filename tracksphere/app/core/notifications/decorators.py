from abc import ABC, abstractmethod


class NotificationComponent(ABC):
    """
    Component Interface for Notification decoration.
    """

    @abstractmethod
    def get_formatted_message(self) -> str:
        raise NotImplementedError


class PlainNotification(NotificationComponent):
    """
    Concrete Base Notification message.
    """

    def __init__(self, raw_message: str):
        self.raw_message = raw_message

    def get_formatted_message(self) -> str:
        return self.raw_message


class NotificationDecorator(NotificationComponent):
    """
    Decorator Pattern:
    Base decorator maintaining a reference to a wrapped NotificationComponent.
    """

    def __init__(self, component: NotificationComponent):
        self._component = component

    def get_formatted_message(self) -> str:
        return self._component.get_formatted_message()


class InAppNotificationDecorator(NotificationDecorator):
    """
    Concrete Decorator:
    Appends in-app visual badges and timestamp styling.
    """

    def __init__(self, component: NotificationComponent, priority_label: str = "INFO"):
        super().__init__(component)
        self.priority_label = priority_label

    def get_formatted_message(self) -> str:
        base_msg = self._component.get_formatted_message()
        return f"[{self.priority_label.upper()}] {base_msg}"


class EmailStyleNotificationDecorator(NotificationDecorator):
    """
    Concrete Decorator:
    Wraps message in structured email-style layout headers and footers.
    """

    def __init__(self, component: NotificationComponent, subject: str = "TrackSphere System Notice"):
        super().__init__(component)
        self.subject = subject

    def get_formatted_message(self) -> str:
        base_msg = self._component.get_formatted_message()
        return f"Subject: {self.subject}\n------------------------\n{base_msg}\n------------------------\nTrackSphere Operations Automated Dispatch"
