import os
import re
from collections import namedtuple
from functools import partial
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from sqlmodel import Session

from app.model import Album, Artist, Song, UnknownArtist

SUPPORTED_MUSIC_EXTENSIONS = ["flac", "mp3", "wav"]


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
    importable = gather_songs(music_path)


def gather_songs(music_path: Path) -> Importable:
    songs = []
    importable = Importable()
    if not music_path.exists():
        raise ValueError("Path given does not exist")
    if not music_path.is_dir():
        raise ValueError("Path is not a directory")
    for dirpath, dirnames, filenames in os.walk(str(music_path)):
        if dirpath == str(music_path):
            pass
        for filename in filenames:
            if extension(filename) in SUPPORTED_MUSIC_EXTENSIONS:
                info_path = dirpath.split(str(music_path))[1:]
                if len(info_path[0].split("/")) == 1:
                    parse_folder_name(info_path[0])
                    song_title = parse_song_file_name(filename)

    return importable


def parse_song_file_name(song_file_name) -> str:
    # Order matters, only the first match is used
    validator_regexes = [r"^[0-9 -]+(.+)$"]
    for validator in validator_regexes:
        match = re.search(song_file_name, validator)
        if match:
            song_title = match.groups()[0]
            return song_title
    raise ValueError("Invalid song file name")


def parse_folder_name(path: str) -> Dict[str, str]:
    # Order matters: the first one found is the first one used
    validator_regexes = [
        (r"^(.+)\(.+\)$", ("album",)),
        (r"^([A-z0-9 ]+).*?(\d+).*?([A-z0-9 ]+)$", ("artist", "year", "album")),
    ]
    validator: Tuple[str, Tuple]
    for validator in validator_regexes:
        match = re.search(validator[0], path)
        if match:
            results = {}
            for name, value in zip(validator[1], match.groups()):
                results[name] = value
            return results
    raise ValueError("Unrecognizable folder name")


def extension(file: str):
    """Returns the extension without the leading dot (e.g. `flac`)"""
    ext = file.rsplit(",", 1)[-1]
    return ext
