from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import Notification
from .base import RepositoryBase


class NotificationRepository(RepositoryBase[Notification]):
    def list(self) -> list[Notification]:
        return self.session.scalars(select(Notification)).all()

    def get(self, notification_id: int) -> Notification | None:
        return self.session.get(Notification, notification_id)

    def create(self, notification: Notification) -> Notification:
        return self.add(notification)

    def update(self, notification: Notification, **changes) -> Notification:
        for key, value in changes.items():
            setattr(notification, key, value)
        self.session.flush()
        return notification

    def delete(self, notification: Notification) -> None:
        super().delete(notification)
