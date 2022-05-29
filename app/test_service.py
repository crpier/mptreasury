from pytest import fixture, mark

from app import import_service
from app.model import UnknownArtist


@fixture
def raw_album_with_one_song() -> import_service.OsWalkResult:
    music_path = "/testdata"
    album_name = "test album"
    walk_result = [
        (
            f"{music_path}/{album_name}",
            [],
            ["01 - First song.flac"],
        )
    ]
    return iter(walk_result)


@fixture
def raw_artist_with_one_album_with_artist_in_dir_name_with_one_song() -> import_service.OsWalkResult:
    music_path = "/testdata"
    artist_name = "test artist"
    album_year = "1986"
    album_name = "test album"
    walk_result = [
        (
            f"{music_path}/{artist_name} - {album_year} - {album_name}",
            [],
            ["01 - First song.flac"],
        )
    ]
    return iter(walk_result)


@fixture
def raw_artist_with_one_album_with_one_song() -> import_service.OsWalkResult:
    music_path = "/testdata"
    artist_name = "test artist"
    album_name = "test album"
    walk_result = [
        (
            f"{music_path}/{artist_name}/{album_name}",
            [],
            ["01 - First song.flac"],
        )
    ]
    return iter(walk_result)


@mark.unit
def test_gather_album_with_one_song(raw_album_with_one_song: import_service.OsWalkResult):
    songs = import_service.gather_songs(raw_album_with_one_song)
    assert songs[0].artist_name == UnknownArtist.name
    assert songs[0].album_name == "test album"
    assert songs[0].title == "First song"
    assert len(songs) == 1


@mark.unit
def test_gather_album_with_artist_in_dir_name_with_one_song(
    raw_artist_with_one_album_with_artist_in_dir_name_with_one_song: import_service.OsWalkResult,
):
    songs = import_service.gather_songs(
        raw_artist_with_one_album_with_artist_in_dir_name_with_one_song
    )
    assert songs[0].artist_name == "test artist"
    assert songs[0].album_name == "test album"
    assert songs[0].title == "First song"
    assert len(songs) == 1


@mark.unit
@mark.skip("Not implemented")
def test_gather_artist_with_one_album(
    raw_artist_with_one_album_with_one_song: import_service.OsWalkResult,
):
    songs = import_service.gather_songs(raw_artist_with_one_album_with_one_song)
    assert songs[0].artist_name == "test artist"
    assert songs[0].album_name == "test album"
    assert songs[0].title == "First song"
    assert len(songs) == 1
