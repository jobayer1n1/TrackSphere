from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import User
from .base import RepositoryBase


class UserRepository(RepositoryBase[User]):
    def list(self) -> list[User]:
        return self.session.scalars(select(User)).all()

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalars(select(User).filter_by(email=email)).first()

    def create(self, user: User) -> User:
        return self.add(user)

    def update(self, user: User, **changes) -> User:
        for key, value in changes.items():
            setattr(user, key, value)
        self.session.flush()
        return user

    def delete(self, user: User) -> None:
        super().delete(user)
