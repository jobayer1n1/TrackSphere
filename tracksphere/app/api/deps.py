from collections.abc import Generator
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth.service import AuthenticationService
from app.core.users.base import User as DomainUser
from app.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User as UserModel
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_optional(
    request: Request,
    auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserModel | None:
    token = None
    # Check Authorization header bearer
    if auth and auth.credentials:
        token = auth.credentials
    # Fallback to session cookie
    elif settings.SESSION_COOKIE_NAME in request.cookies:
        token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if not token:
        return None

    auth_service = AuthenticationService.get_instance()
    domain_user = auth_service.validate_session(db, token)
    if not domain_user:
        return None

    user_repo = UserRepository(db)
    return user_repo.get(domain_user.user_id)


def get_current_user(
    user: UserModel | None = Depends(get_current_user_optional),
) -> UserModel:
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden for role {current_user.role.value}. Required: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
