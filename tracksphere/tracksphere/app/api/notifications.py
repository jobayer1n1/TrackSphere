from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..repositories.notification_repository import NotificationRepository
from ..schemas import NotificationRead

router = APIRouter()


@router.get("/", response_model=list[NotificationRead])
def list_notifications(db: Session = Depends(get_db)):
    repository = NotificationRepository(db)
    return repository.list()
