import os
import shutil
from pathlib import Path

import pytest

from app import import_service, model


@pytest.fixture
def album_folder_with_subfolder(tmp_path: Path):
    for song in ["test1.flac", "test2.flac", "test3.flac", "test4.flac"]:
        with (tmp_path / song).open("w"):
            pass
    os.mkdir(tmp_path / "covers")
    yield tmp_path
    shutil.rmtree(tmp_path)


def test_determine_folder_type_many_songs(album_folder_with_cue_file):
    """Test that an album folder is identified when it has many music files
    and a subfolder"""
    folder_type = import_service.determine_folder_type(album_folder_with_cue_file)
    assert folder_type == import_service.FolderType.album_folder


@pytest.fixture
def album_folder_with_cue_file(tmp_path: Path):
    with (tmp_path / "test.cue").open("w"):
        pass
    with (tmp_path / "test.flac").open("w"):
        pass
    for subfolder in ["art", "covers", "misc"]:
        os.mkdir(tmp_path / subfolder)
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.fixture
def artist_folder(tmp_path: Path):
    for album in ["test_album_1", "test_album_2", "test_album_3"]:
        os.mkdir(tmp_path / album)
    yield tmp_path
    shutil.rmtree(tmp_path)


def test_determine_folder_type_cue_album(album_folder_with_subfolder):
    """Test that an album folder is identified when it has a cue file
    and a music file regardless of number of subfolders"""
    folder_type = import_service.determine_folder_type(album_folder_with_subfolder)
    assert folder_type == import_service.FolderType.album_folder


def test_determine_folder_type_artist_folder(artist_folder):
    """Test that an artist folder is identified when it has many subfolders
    and no songs"""
    folder_type = import_service.determine_folder_type(artist_folder)
    assert folder_type == import_service.FolderType.artist_folder


# TODO: parametrize non-ASCII names
@pytest.fixture
def song_with_non_ascii_album(tmp_path):
    song_path = tmp_path / "01 - Test Title.flac"
    with song_path.open("w"):
        pass
    yield model.Song(
        title="Test Title",
        album_name="Ǹ Test Album",
        artist_name="Test Artist",
        local_path=song_path,
    )
    try:
        shutil.rmtree(tmp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def library_folder(tmp_path):
    yield tmp_path
    try:
        shutil.rmtree(tmp_path)
    except FileNotFoundError:
        pass


def test_copy_songs_to_music_folder_non_ascii_album(
    song_with_non_ascii_album: model.Song, library_folder: Path
):
    """Test that album with non-ASCII name is copied to a path with similar ASCII name"""
    import_service.copy_songs_to_music_folder(
        [song_with_non_ascii_album], library_folder
    )
    assert str(song_with_non_ascii_album.local_path).encode("ascii")
    assert "/N Test Album/" in str(song_with_non_ascii_album.local_path)


# TODO: parametrize non-ASCII names
@pytest.fixture
def song_with_non_ascii_title(tmp_path: Path):
    song_path = tmp_path / "01 - Ǹ Test Title.flac"
    with song_path.open("w"):
        pass
    yield model.Song(
        title="Ǹ Test Title",
        album_name="Test Album",
        artist_name="Test Artist",
        local_path=song_path,
    )
    try:
        shutil.rmtree(tmp_path)
    except FileNotFoundError:
        pass


def test_copy_songs_to_music_folder_non_ascii_title(
    song_with_non_ascii_title: model.Song, library_folder: Path
):
    """Test that song with non-ASCII title is saved in file with ASCII name"""
    import_service.copy_songs_to_music_folder(
        [song_with_non_ascii_title], library_folder
    )
    assert str(song_with_non_ascii_title.local_path).encode("ascii")
    assert str(song_with_non_ascii_title.local_path).endswith("/N Test Title.flac")
