from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.base import RepositoryBase


class NotificationRepository(RepositoryBase[Notification]):
    def list(self) -> List[Notification]:
        return list(
            self.session.scalars(
                select(Notification).order_by(Notification.timestamp.desc())
            ).all()
        )

    def list_by_user(self, user_id: int) -> List[Notification]:
        return list(
            self.session.scalars(
                select(Notification)
                .where(Notification.recipient_id == user_id)
                .order_by(Notification.timestamp.desc())
            ).all()
        )

    def get(self, notification_id: int) -> Optional[Notification]:
        return self.session.get(Notification, notification_id)

    def create(self, notification: Notification) -> Notification:
        return self.add(notification)

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        notification = self.get(notification_id)
        if notification:
            notification.read = True
            self.session.flush()
            self.session.commit()
            self.session.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        notifications = self.list_by_user(user_id)
        count = 0
        for n in notifications:
            if not n.read:
                n.read = True
                count += 1
        self.session.flush()
        self.session.commit()
        return count
