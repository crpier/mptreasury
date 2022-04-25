import os
import re
from functools import partial
from pathlib import Path
from typing import Iterator, List, Optional, Tuple, Dict
from attr import validate
from app import db, discogs_adapter


from app.model import Album, Artist, RawAlbum, RawSong, Song, UnknownArtist

SUPPORTED_MUSIC_EXTENSIONS = ["flac", "mp3", "wav"]

# Damn, os.walk has quite the result. And this is a simplified version 😵
OsWalkResult = Iterator[Tuple[str, List[str], List[str]]]


def import_songs(music_path: Path, session):
    validate_music_path(music_path)
    music_path = music_path.absolute()
    walk_result: OsWalkResult = os.walk(str(music_path))
    importable = gather_songs(walk_result)
    raw_album = RawAlbum(importable)
    discogs = discogs_adapter.DiscogsAdapter()
    songs, album = discogs.populate_raw_album(raw_album)
    if not db.album_exists(album, session):
        db.add_album(album, session)
        db.add_songs(songs, session)


def validate_music_path(music_path: Path):
    if not music_path.exists():
        raise ValueError("Path given does not exist")
    if not music_path.is_dir():
        raise ValueError("Path is not a directory")


def request_songs_in_album_data(songs: List[RawSong]):
    pass


def gather_songs(walked_path: OsWalkResult) -> List[RawSong]:
    raw_songs: List[RawSong] = []
    for dirpath, _, filenames in walked_path:
        for filename in filenames:
            if extension(filename) in SUPPORTED_MUSIC_EXTENSIONS:
                path_basename = os.path.basename(dirpath)
                folder_dict = parse_folder_name(path_basename)
                song_title = parse_song_file_name(filename)
                song = RawSong(
                    title=song_title,
                    path=Path(dirpath + "/" + filename),
                    album_name=folder_dict["album"],
                    artist_name=folder_dict.get("artist", UnknownArtist.name),
                )
                raw_songs.append(song)

    if len(raw_songs) == 0:
        raise ValueError("no valid songs in path")
    return raw_songs


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
