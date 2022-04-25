from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy import orm, MetaData
from sqlalchemy.sql.schema import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy import types
from typing import List, Any

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
engine = create_engine(config.DB_URI, echo=True)
Session = sessionmaker(engine)


def create_tables(engine):
    mapper_registry.metadata.create_all(engine)
    MetaData().create_all(engine)


def album_exists(album: Album, Session):
    with Session(future=True) as session:
        existing_album = session.execute(
            select(Album).filter_by(master_provider_id=album.master_provider_id)
        ).first()
        return bool(existing_album)


def add_album(album: Album, Session):
    with Session() as session:
        session.add(album)
        session.commit()


def add_songs(songs: List[Song], Session):
    with Session() as session:
        for song in songs:
            session.add(song)
        session.commit()


def song_exists(song: Song, Session: orm.Session):
    return False
