import sqlite3
import textwrap
from pathlib import Path
from typing import Any, List

from app.config import Config
from app.model import Album, Song


def connect(db_file: Path):
    conn = sqlite3.connect(db_file)
    return conn


def create_songs_table(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS songs (
            id integer PRIMARY KEY,
            title text NOT NULL,
            local_path text NOT NULL,
            remote_path text NOT NULL,
            album_name text NOT NULL,
            artist_name text NOT NULL
        );"""
    )


def create_albums_table(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS albums (
            id integer PRIMARY KEY,
            name text NOT NULL,
            genre text NOT NULL,
            released integer NOT NULL,
            artist_id integer NOT NULL,
            artist_name text NOT NULL,
            provider_id integer NOT NULL,
            master_name text NOT NULL,
            master_provider_id integer NOT NULL
        );"""
    )


def create_tables(config: Config):
    conn = connect(config.DB_FILE)
    create_songs_table(conn)
    create_albums_table(conn)


def get_album_id(album: Album, Session) -> int | None:
    return 0


def add_album_and_songs(album: Album, songs: List[Song], Session):
    ...
