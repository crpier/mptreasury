from sqlalchemy import create_engine
from sqlalchemy.orm import registry
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String

from app.config import config
from app.model import Song

mapper_registry = registry()
songs_table = Table(
    "songs",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("path", String),
    Column("provider_id", Integer, index=True),
    Column("album_name", String, index=True),
    Column("artist_name", String),
)


mapper_registry.map_imperatively(Song, songs_table)
engine = create_engine(config.DB_URI, echo=True)
session_factory = sessionmaker(bind=engine)
# TODO:does this work, really?
# sqlalchemy.MetaData().create_all(engine)
