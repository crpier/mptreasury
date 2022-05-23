from pathlib import Path
from typing import Any, List

from sqlalchemy import MetaData, create_engine, orm, select, types
from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy.sql.schema import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String
from app.config import Config

from app.config import config
from app.model import Album, Song


class PathType(types.TypeDecorator):
    impl = String

    def process_bind_param(self, value: Path, dialect) -> Any:
        return str(value)

    def process_result_value(self, value: str, dialect) -> Path:
        return Path(value)


mapper_registry = registry()
songs_table = Table(
    "songs",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("path", PathType),
    Column("album_name", String, index=True),
    Column("artist_name", String),
)

albums_table = Table(
    "albums",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("genre", String),
    Column("released", Integer),
    Column("artist_id", Integer),
    Column("artist_name", String),
    Column("provider_id", Integer, index=True),
    Column("master_name", String),
    Column("master_provider_id", Integer),
)

mapper_registry.map_imperatively(Album, albums_table)
mapper_registry.map_imperatively(Song, songs_table)
master_engine = None


def get_sessionmaker(settings: Config):
    global master_engine
    master_engine = create_engine(settings.DB_URI, echo=True)
    maker = sessionmaker(master_engine, expire_on_commit=False)
    return maker


def create_tables():
    global master_engine
    if master_engine is None:
        raise ValueError("There was no engine initialized")
    mapper_registry.metadata.create_all(master_engine)
    MetaData().create_all(master_engine)


def album_exists(album: Album, Session):
    with Session(future=True) as session:
        existing_album = session.execute(
            select(Album).filter_by(master_provider_id=album.master_provider_id)
        ).first()
        return bool(existing_album)


def add_album_and_songs(album: Album, songs: List[Song], Session):
    with Session() as session:
        session.add(album)
        for song in songs:
            session.add(song)


def add_album(album: Album, Session):
    with Session() as session:
        session.add(album)
        session.commit()


def add_songs(songs: List[Song], Session):
    with Session() as session:
        for song in songs:
            session.add(song)
        session.commit()


def update_song(song: Song, Session):
    with Session() as session:
        session.add(song)
        session.commit()
