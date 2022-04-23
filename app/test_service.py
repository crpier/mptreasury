from functools import lru_cache, partial
from pathlib import Path
import os
import shutil

from pytest import fixture, mark
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app import service
from app.model import Album, Artist, Song, UnknownArtist


@lru_cache
@fixture
def in_memory_engine():
    dsn = "sqlite:///:memory"
    engine = create_engine(dsn, echo=True)
    return engine


@fixture
def sessionmaker(in_memory_engine: Engine):
    partial_func = partial(Session, in_memory_engine)
    return partial_func


@fixture
def raw_album_with_one_song():
    album_name = "test album"
    test_album_path_name = f"./tests/testdata/{album_name}"
    test_songs_names = [
        "01 - First song.flac",
    ]
    os.makedirs(test_album_path_name)
    for song_path_name in test_songs_names:
        song_path = Path(os.path.join(test_album_path_name, song_path_name))
        song_path.touch()
    yield Path(test_album_path_name).absolute()
    shutil.rmtree(test_album_path_name)


@fixture
def raw_artist_with_one_album_with_artist_in_dir_name_with_one_song():
    artist_name = "test artist"
    album_name = "test album"
    test_album_path_name = f"./tests/testdata/{artist_name} - 1986 - {album_name}"
    test_songs_names = [
        "01 - First song.flac",
    ]
    os.makedirs(test_album_path_name)
    for song_path_name in test_songs_names:
        song_path = Path(os.path.join(test_album_path_name, song_path_name))
        song_path.touch()
    yield Path(test_album_path_name).absolute()
    shutil.rmtree(test_album_path_name)


@fixture
def raw_artist_with_one_album_with_one_song():
    artist_name = "test artist"
    album_name = "test_album"
    test_artist_path_name = f"./tests/testdata/{artist_name}"
    test_album_path_name = os.path.join(test_artist_path_name, album_name)
    song_file_name = "01 - First song.flac"
    os.makedirs(test_album_path_name)
    song_path = Path(os.path.join(test_album_path_name, song_file_name))
    song_path.touch()
    yield Path(test_album_path_name).absolute()
    shutil.rmtree(test_artist_path_name)


def test_gather_album_with_one_song(raw_album_with_one_song: Path):
    songs = service.gather_songs(raw_album_with_one_song)
    assert songs._songs[0].artist is UnknownArtist
    assert songs._songs[0].album.name == "test album"
    assert songs._songs[0].title == "First song"
    assert len(songs._songs) == 1
    assert not songs.is_empty()


def test_gather_album_with_artist_in_dir_name_with_one_song(
    raw_artist_with_one_album_with_artist_in_dir_name_with_one_song: Path,
):
    songs = service.gather_songs(
        raw_artist_with_one_album_with_artist_in_dir_name_with_one_song
    )
    assert songs._songs[0].artist.name == "test artist"
    assert songs._songs[0].album.name == "test album"
    assert songs._songs[0].title == "First song"
    assert len(songs._songs) == 1
    assert not songs.is_empty()


@mark.skip("Not implemented")
def test_gather_artist_with_one_album(raw_artist_with_one_album_with_one_song: Path):
    songs = service.gather_songs(raw_artist_with_one_album_with_one_song)
    assert songs._songs[0].artist.name == "test artist"
    assert songs._songs[0].album.name == "test album"
    assert songs._songs[0].title == "First song"
    assert len(songs._songs) == 1
    assert not songs.is_empty()
