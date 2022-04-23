from functools import lru_cache, partial
from pathlib import Path
import os

from pytest import fixture
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine, select

from app import service
from app.model import Album, Artist, Song


@lru_cache
@fixture
def in_memory_engine():
    dsn = "sqlite:///:memory"
    engine = create_engine(dsn, echo=True)
    return engine


@fixture
def sessionmaker(in_memory_engine: Engine):
    partial_func = partial(Session, in_memory_engine)
    return partial_func


def test_gather_looks_no_more_than_2_levels_down():
    os.makedirs()
    service.gather_songs()
