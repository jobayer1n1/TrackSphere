from sqlalchemy import select

from app.infrastructure.database import init_db
from app.models import User, Driver, Vehicle, Delivery, Notification, Location


def test_database_initialization(database_module):
    assert database_module.engine is not None
    assert database_module.SessionLocal is not None


def test_seed_data_loaded(db_session):
    users = db_session.scalars(select(User)).all()
    drivers = db_session.scalars(select(Driver)).all()
    vehicles = db_session.scalars(select(Vehicle)).all()
    deliveries = db_session.scalars(select(Delivery)).all()
    notifications = db_session.scalars(select(Notification)).all()
    locations = db_session.scalars(select(Location)).all()

    assert any(user.role == "ADMINISTRATOR" for user in users)
    assert any(user.role == "DISPATCHER" for user in users)
    assert sum(1 for user in users if user.role == "DRIVER") >= 2
    assert len(vehicles) >= 2
    assert len(deliveries) >= 3
    assert len(notifications) >= 2
    assert len(locations) >= 2
