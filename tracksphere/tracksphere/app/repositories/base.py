from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class RepositoryBase(Generic[T]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
        self.session.flush()
