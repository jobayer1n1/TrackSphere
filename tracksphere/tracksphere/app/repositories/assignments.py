from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from tracksphere.app.models import Assignment, AssignmentStatus


class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_assignment(
        self,
        delivery_id: int,
        driver_id: int,
        vehicle_id: int | None = None,
        status: AssignmentStatus = AssignmentStatus.PENDING,
    ) -> Assignment:
        assignment = Assignment(
            delivery_id=delivery_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            status=status,
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        return self.db.query(Assignment).filter(Assignment.id == assignment_id).first()

    def list_assignments(self):
        return self.db.scalars(select(Assignment)).all()
