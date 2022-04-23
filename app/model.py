import datetime
from pathlib import Path
from typing import Optional, List

from sqlmodel import Field, SQLModel
from sqlmodel.main import Relationship


class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    genre: Optional[str] = Field(default=None, nullable=False)
    released: Optional[datetime.datetime] = Field(default=None, nullable=False)
    """TODO: custom type that ensures
    - path is absolute
    - optionally, has a prefix"""
    path: Path

    album_id: Optional[int] = Field(foreign_key="album.id", nullable=False, default=None)
    album_name: Optional[str] = Field(index=True, nullable=False, default=None)
    artist_id: Optional[int] = Field(foreign_key="artist.id", nullable=False, default=None)
    artist_name: Optional[str] = Field(index=True, nullable=False, default=None)

    album: "Album" = Relationship(back_populates="songs")
    artist: "Artist" = Relationship(back_populates="songs")


class Album(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    genre: Optional[str] = Field(nullable=False, default=None)
    released: Optional[datetime.datetime] = Field(nullable=False, default=None)

    artist_id: Optional[int] = Field(
        nullable=False, foreign_key="artist.id", default=None
    )
    artist_name: Optional[str] = Field(nullable=False, index=True, default=None)

    artist: "Artist" = Relationship(back_populates="albums")
    songs: List[Song] = Relationship(back_populates="album")


class Artist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    albums: List[Album] = Relationship(back_populates="album")
    songs: List[Song] = Relationship(back_populates="artist")


UnknownArtist = Artist(id=-1, name="Unkown Artist")
