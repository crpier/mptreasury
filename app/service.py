import os
import re
import shutil
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

from app import db, discogs_adapter
from app.metadata_adapter import update_metadata
from app.model import RawAlbum, RawSong, Song, UnknownArtist

SUPPORTED_MUSIC_EXTENSIONS = ["flac", "mp3", "wav"]

# Damn, os.walk has quite the 😵 result type. And this is a simplified version
OsWalkResult = Iterator[Tuple[str, List[str], List[str]]]


def import_songs(
    music_path: Path,
    Session,
    root_music_path: Path,
    metadata_retriever: discogs_adapter.DiscogsAdapter,
):
    songs = import_songs_data(music_path, Session, metadata_retriever)
    for song in songs:
        update_metadata(song)
        move_song(song, Session, root_music_path)


def move_song(song: Song, Session, root_music_path: Path):
    target_folder = Path(f"{root_music_path}/{song.artist_name}/{song.album_name}")
    if not target_folder.exists():
        os.makedirs(target_folder)
    file_name = os.path.basename(song.path)
    target_path = target_folder / file_name
    shutil.move(song.path, target_path)
    song.path = target_path
    db.update_song(song, Session)


def import_songs_data(
    music_path: Path, session, metadata_retriever: discogs_adapter.DiscogsAdapter
):
    validate_music_path(music_path)
    music_path = music_path.absolute()
    walk_result: OsWalkResult = os.walk(str(music_path))
    importable = gather_songs(walk_result)
    raw_album = RawAlbum(importable)
    songs, album = metadata_retriever.populate_raw_album(raw_album)
    if not db.album_exists(album, session):
        db.add_album_and_songs(album, songs, session)
    return songs


def validate_music_path(music_path: Path):
    if not music_path.exists():
        raise ValueError("Path given does not exist")
    if not music_path.is_dir():
        raise ValueError("Path is not a directory")


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
