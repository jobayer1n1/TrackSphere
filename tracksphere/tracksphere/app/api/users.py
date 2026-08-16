from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..repositories.user_repository import UserRepository
from ..schemas import UserRead

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    repository = UserRepository(db)
    return repository.list()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
