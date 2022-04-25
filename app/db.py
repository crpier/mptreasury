from sqlalchemy import create_engine, MetaData, select
from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy import orm
from sqlalchemy.sql.schema import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String
from typing import List

from app.config import config
from app.model import Album, Song

mapper_registry = registry()
songs_table = Table(
    "songs",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("path", String),
    Column("album_name", String, index=True),
    Column("artist_name", String),
)

albums_table = Table(
    "albums",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("master_name", String),
    Column("provider_id", Integer, index=True),
    Column("artist_name", String),
)

mapper_registry.map_imperatively(Album, albums_table)
mapper_registry.map_imperatively(Song, songs_table)
engine = create_engine(config.DB_URI, echo=True)
Session = sessionmaker(engine)
# TODO:does this work, really?
MetaData().create_all(engine)


def album_exists(album: Album, Session: sessionmaker[orm.Session]):
    with Session(future=True) as session:
        existing_album = session.execute(
            select(Album).filter_by(master_provider_id=album.master_provider_id)
        ).first()
        return bool(existing_album)

def add_album(album: Album, Session: sessionmaker[orm.Session]):
    with Session() as session:
        session.add(album)
        session.commit()

def add_songs(songs: List[Song], Session: sessionmaker[orm.Session]):
    with Session() as session:
        for song in songs:
            session.add(song)
        session.commit()

def song_exists(song: Song, Session: sessionmaker[orm.Session]):
    return False
