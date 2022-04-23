import os
import re
from functools import partial
from pathlib import Path
from typing import Iterator, List, Optional, Tuple, Dict

from sqlmodel import Session

from app.model import Album, Artist, Song, UnknownArtist

SUPPORTED_MUSIC_EXTENSIONS = ["flac", "mp3", "wav"]

# Damn, os.walk has quite the result. And this is the simplified version 😵
OsWalkResult = Iterator[Tuple[str, List[str], List[str]]]

class Importable:
    def __init__(self):
        self._songs: List[Song] = []
        self._emtpy = True

    def add_song(
        self, title: str, path: Path, album_name: str, artist_name: Optional[str] = None
    ):
        if artist_name is None:
            artist = UnknownArtist
        else:
            artist = Artist(name=artist_name)

        album = Album(name=album_name, artist=artist)
        song = Song(title=title, path=path, album=album, artist=artist)
        self._songs.append(song)
        self._emtpy = False

    def is_empty(self):
        return self._emtpy


def import_songs(music_path: Path, sessionmaker: partial[Session]):
    if not music_path.exists():
        raise ValueError("Path given does not exist")
    if not music_path.is_dir():
        raise ValueError("Path is not a directory")
    music_path = music_path.absolute()
    walk_result: OsWalkResult = os.walk(str(music_path))
    importable = gather_songs(walk_result)
    songs_ready_for_import = gather_data(importable)
    with sessionmaker() as session:
        for song in songs_ready_for_import:
            session.add(song)
        session.commit()


def gather_data(importable: Importable) -> List[Song]:
    return list(importable._songs)


def gather_songs(walked_path: OsWalkResult) -> Importable:
    importable = Importable()
    for dirpath, _, filenames in walked_path:
        for filename in filenames:
            if extension(filename) in SUPPORTED_MUSIC_EXTENSIONS:
                path_basename = os.path.basename(dirpath)
                folder_dict = parse_folder_name(path_basename)
                song_title = parse_song_file_name(filename)
                importable.add_song(
                    title=song_title,
                    path=Path(dirpath + "/" + filename),
                    album_name=folder_dict["album"],
                    artist_name=folder_dict.get("artist", None),
                )

    if importable.is_empty():
        raise ValueError("no valid songs in path")
    return importable


def parse_song_file_name(song_file_name) -> str:
    # Order matters, only the first match is used
    validator_regexes = [r"^[0-9 -]+(.+)\..+$"]
    for validator in validator_regexes:
        match = re.search(validator, song_file_name)
        if match:
            song_title = match.groups()[0]
            return song_title.strip()
    raise ValueError("Invalid song file name")


def parse_folder_name(path: str) -> Dict[str, str]:
    # Order matters: the first one found is the first one used
    validator_regexes = [
        (r"^(.+)\(.+\)$", ("album",)),
        (r"^([A-z0-9 ]+).*?(\d+).*?([A-z0-9 ]+)$", ("artist", "year", "album")),
        (r"^(.+)$", ("album",)),
    ]
    validator: Tuple[str, Tuple]
    for validator in validator_regexes:
        match = re.search(validator[0], path)
        if match:
            results = {}
            for name, value in zip(validator[1], match.groups()):
                results[name] = value.strip()
            return results
    raise ValueError("Unrecognizable folder name")


def extension(file: str):
    """Returns the extension without the leading dot (e.g. `flac`)"""
    ext = file.rsplit(".", 1)[-1]
    return ext
