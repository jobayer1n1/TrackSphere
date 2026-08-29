from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment
from app.repositories.base import RepositoryBase


class AssignmentRepository(RepositoryBase[Assignment]):
    def list(self) -> List[Assignment]:
        return list(
            self.session.scalars(
                select(Assignment)
                .options(joinedload(Assignment.delivery), joinedload(Assignment.driver), joinedload(Assignment.vehicle))
                .order_by(Assignment.assigned_at.desc())
            ).all()
        )

    def get(self, assignment_id: int) -> Optional[Assignment]:
        return self.session.scalars(
            select(Assignment)
            .options(joinedload(Assignment.delivery), joinedload(Assignment.driver), joinedload(Assignment.vehicle))
            .where(Assignment.id == assignment_id)
        ).first()

    def get_by_delivery(self, delivery_id: int) -> Optional[Assignment]:
        return self.session.scalars(
            select(Assignment)
            .options(joinedload(Assignment.driver), joinedload(Assignment.vehicle))
            .where(Assignment.delivery_id == delivery_id)
        ).first()

    def create(self, assignment: Assignment) -> Assignment:
        return self.add(assignment)

    def update(self, assignment: Assignment, **changes) -> Assignment:
        for key, value in changes.items():
            if value is not None:
                setattr(assignment, key, value)
        self.session.flush()
        self.session.commit()
        self.session.refresh(assignment)
        return assignment
