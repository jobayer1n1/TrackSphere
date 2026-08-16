import importlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "tracksphere") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "tracksphere"))


@pytest.fixture(scope="session")
def database_module():
    with tempfile.TemporaryDirectory() as temp_dir:
        database_url = f"sqlite:///{os.path.join(temp_dir, 'tracksphere_test.db')}"
        os.environ["TRACKSPHERE_ENV"] = "test"
        os.environ["DATABASE_URL"] = database_url

        from app.infrastructure.config import ConfigurationManager

        ConfigurationManager.reset_instance()

        import app.infrastructure.database as database
        importlib.reload(database)
        database.init_db()
        try:
            yield database
        finally:
            database.engine.dispose()


@pytest.fixture
def db_session(database_module):
    with database_module.SessionLocal() as session:
        yield session
