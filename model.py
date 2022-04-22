from pathlib import Path, Any
from typing import NewType
import datetime

song_id = NewType("song_id", int)
album_id = NewType("album_id", int)
artist_id = NewType("artist_id", int)

class Song:
    id: song_id
    title: str
    genre: str
    released: datetime.datetime
    """TODO: custom type that ensures
    - path is absolute
    - optionally, has a prefix"""
    path: Path

    album_id: album_id
    album_name: str
    artist_id: artist_id
    artist_name: artist_id


class Album:
    id: album_id
    genre: str
    released: datetime.datetime

    artist_id: artist_id
    artist_name: str


class Artist:
    id: artist_id
    name: str
