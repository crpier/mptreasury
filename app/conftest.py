import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app import db


@pytest.fixture
def in_memory_engine():
    engine = create_engine("sqlite://")
    db.create_tables(engine)
    return engine


@pytest.fixture
def memory_session(in_memory_engine):
    Session = sessionmaker(in_memory_engine)
    return Session
