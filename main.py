from pathlib import Path, Any
from typing import NewType
import datetime

song_id = NewType("song_id", int)
album_id = NewType("album_id", int)
artist_id = NewType("artist_id", int)

class Song:
    id: song_id
    path: Path
    album_id: album_id
    art_path: Path
    art_is_embedded: bool

    title: str
    artist: artist_id
    album: str
    genre: str
    subgenre: str
    provider_id: Any
    release: datetime.datetime
    lyrics: Any
    release_type: Any
    length: datetime.timedelta
    bitrate: int
# needs custom type I think
    samplerate: int


class Album:
    id: album_id
    artist: artist_id
    genre: str
    release: datetime.datetime
    provider_id: Any

class Artist:
    id: artist_id
