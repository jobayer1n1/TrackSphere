import os
import secrets
from pathlib import Path
from dotenv import load_dotenv


from threading import Lock


# `config.py` lives in tracksphere/app/infrastructure.  Keep runtime files at
# the repository root so application startup does not depend on the shell CWD.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_DATABASE_FILE = PROJECT_ROOT / "tracksphere.db"


class SingletonMeta(type):
    _instances: dict[type, object] = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def _reset_instance(cls):
        with cls._lock:
            cls._instances.pop(cls, None)


class ConfigurationManager(metaclass=SingletonMeta):
    """Application-wide configuration manager.

    Using a Singleton for configuration ensures one shared view of environment
    and application settings across the TrackSphere process.

    This is appropriate because configuration values are global, stable after
    startup, and accessed by multiple layers such as database initialization
    and application services.

    Limitations:
    - Singleton state is global and can make tests harder without explicit reset.
    - It is not suitable for per-request or multi-tenancy scoped configuration.
    """

    def __init__(self, env_path: str | None = None):
        env_file = Path(env_path) if env_path is not None else DEFAULT_ENV_FILE
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
        self.environment = os.getenv("TRACKSPHERE_ENV", "development")
        self.database_url = os.getenv(
            "DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_FILE.as_posix()}"
        )
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))

    @classmethod
    def reset_instance(cls):
        SingletonMeta._instances.pop(cls, None)

    def as_dict(self) -> dict[str, str]:
        return {
            "environment": self.environment,
            "database_url": self.database_url,
        }
