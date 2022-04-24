import datetime
from pathlib import Path
from typing import Optional


class RawSong:
    def __init__(self, title: str, album_name: str, artist_name: Optional[str] = None):
        self.title = title
        self.album_name = album_name
        self.artist_name = artist_name


class Song:
    def __init__(
        self,
        id: int,
        title: str,
        # genre: str,
        # released: datetime.datetime,
        path: Path,
        # album_id: int,
        album_name: str,
        # artist_id: int,
        artist_name: str,
        provider_id: Optional[int] = None,
    ):
        self.id = id
        self.title = title
        # self.genre = genre
        # self.released = released
        """TODO: custom type that ensures
        - path is absolute
        - optionally, has a prefix"""
        self.path = path
        # self.album_id = album_id
        self.album_name = album_name
        # self.artist_id = artist_id
        self.artist_name = artist_name
        self.provider_id = provider_id


class Album:
    def __init__(
        self,
        id: int,
        name: str,
        genre: str,
        released: datetime.datetime,
        artist_id: int,
        artist_name: str,
        master_provider_id: Optional[int] = None,
        master_name: Optional[str] = None,
        provider_id: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.genre = genre
        self.released = released
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.master_provider_id = master_provider_id
        self.master_name = master_name
        self.provider_id = provider_id


class Artist:
    def __init__(self, id: int, name: str, provider_id: Optional[int] = None):
        self.id = id
        self.name = name
        self.provider_id = provider_id


UnknownArtist = Artist(id=-1, name="Unkown Artist")
