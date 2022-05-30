from pathlib import Path
from typing import List, Optional


class RawSong:
    def __init__(
        self, title: str, album_name: str, path: Path, artist_name: Optional[str] = None
    ):
        self.title = title
        self.album_name = album_name
        self.artist_name = artist_name
        self.path = path


class RawAlbum:
    def __init__(self, songs: List[RawSong]):
        self.name = songs[0].album_name
        self.artist_name = songs[0].artist_name
        self.track_names: List[str] = []
        self.songs: List[RawSong] = []
        for song in songs:
            self._validate_song(song)
            self.track_names.append(song.title)
            self.songs.append(song)

    def _validate_song(self, song: RawSong):
        if song.artist_name != self.artist_name:
            raise ValueError("song does not have same artist as album")
        if song.album_name != self.name:
            raise ValueError("song does not have same album_name as album")

    def song_by_title(self, title: str):
        for song in self.songs:
            if song.title == title:
                return song


class Album:
    def __init__(
        self,
        name: str,
        genre: str,
        released: int,
        artist_id: int,
        artist_name: str,
        master_provider_id: int,
        master_name: str,
        provider_id: int,
        id: Optional[int] = None,
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


class Song:
    title: str
    album_name: str

    def __init__(
        self,
        title: str,
        # track_number
        # genre: str,
        # released: datetime.datetime,
        path: Path,
        # album_id: int,
        album_name: str,
        # artist_id: int,
        artist_name: str,
        album: Optional[Album] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.title = title
        # self.genre = genre
        # self.released = released
        """TODO: custom type that ensures
        - optionally, has a prefix"""
        self.path = path.absolute()
        # self.album_id = album_id
        self.album_name = album_name
        # self.artist_id = artist_id
        self.artist_name = artist_name
        self.album = album

    def printable_dict(self):
        return dict(
                id= self.id,
                title= self.title,
                album_name= self.album_name,
                artist_name= self.artist_name,
                path= str(self.path),
                )

UnknownArtist = Artist(id=-1, name="Unkown Artist")
