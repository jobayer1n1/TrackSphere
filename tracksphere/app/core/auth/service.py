from threading import Lock
from sqlalchemy.orm import Session

from app.core.auth.security import create_access_token, decode_access_token, verify_password
from app.core.users.base import User as DomainUser
from app.core.users.factory import UserFactory
from app.models.user import User as UserModel
from app.repositories.user_repository import UserRepository


class AuthenticationService:
    """
    Singleton Pattern:
    AuthenticationService provides a centralized, thread-safe instance
    for authenticating credentials, validating JWT/cookie sessions, and mapping users to domain classes.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AuthenticationService, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "AuthenticationService":
        """Access the centralized Singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def authenticate(self, db: Session, email: str, password: str) -> tuple[UserModel | None, str | None]:
        """Verify user credentials and generate access token."""
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(email)

        if not user or not user.active:
            return None, None

        if not verify_password(password, user.password_hash):
            return None, None

        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
        }
        token = create_access_token(token_data)
        return user, token

    def validate_session(self, db: Session, token: str) -> DomainUser | None:
        """Validate token and return Domain User instance instantiated by UserFactory."""
        payload = decode_access_token(token)
        if not payload:
            return None

        user_id = int(payload.get("user_id", payload.get("sub", 0)))
        if not user_id:
            return None

        user_repo = UserRepository(db)
        db_user = user_repo.get(user_id)
        if not db_user or not db_user.active:
            return None

        driver_id = db_user.driver.id if db_user.driver else None
        license_num = db_user.driver.license_number if db_user.driver else None

        domain_user = UserFactory.create_user(
            role=db_user.role,
            user_id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            active=db_user.active,
            driver_id=driver_id,
            license_number=license_num,
        )
        return domain_user
