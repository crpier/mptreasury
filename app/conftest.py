import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app import db
from app.bootstrap import bootstrap


@pytest.fixture
def fake_settings():
    return bootstrap("e2e_test")


@pytest.fixture
def memory_session(fake_settings):
    Session = db.get_sessionmaker(fake_settings)
    db.create_tables()
    return Session
