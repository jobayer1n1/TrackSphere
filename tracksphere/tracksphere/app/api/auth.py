from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..repositories.user_repository import UserRepository
from ..application.auth import create_session_token, verify_password, verify_session_token
from ..models import User

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

SESSION_COOKIE_NAME = "tracksphere_session"


def _get_user_by_cookie(request: Request, db: Session) -> User | None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    user_id = verify_session_token(token)
    if user_id is None:
        return None
    return UserRepository(db).get(user_id)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = _get_user_by_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.post("/login")
def login(response: Response, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_session_token(user.id)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(SESSION_COOKIE_NAME, token, httponly=True)
    return response


@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
