from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import RepositoryBase


class UserRepository(RepositoryBase[User]):
    def list(self) -> List[User]:
        return list(self.session.scalars(select(User).order_by(User.id)).all())

    def get(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.scalars(select(User).where(User.email == email)).first()

    def create(self, user: User) -> User:
        return self.add(user)

    def update(self, user: User, **changes) -> User:
        for key, value in changes.items():
            if value is not None:
                setattr(user, key, value)
        self.session.flush()
        self.session.commit()
        self.session.refresh(user)
        return user
