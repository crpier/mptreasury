from pytest import fixture, mark

from app import service
from app.model import UnknownArtist


@fixture
def raw_album_with_one_song() -> service.OsWalkResult:
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
def raw_artist_with_one_album_with_artist_in_dir_name_with_one_song() -> service.OsWalkResult:
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
def raw_artist_with_one_album_with_one_song() -> service.OsWalkResult:
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
def test_gather_album_with_one_song(raw_album_with_one_song: service.OsWalkResult):
    songs = service.gather_songs(raw_album_with_one_song)
    assert songs._songs[0].artist is UnknownArtist
    assert songs._songs[0].album.name == "test album"
    assert songs._songs[0].title == "First song"
    assert len(songs._songs) == 1
    assert not songs.is_empty()


@mark.unit
def test_gather_album_with_artist_in_dir_name_with_one_song(
    raw_artist_with_one_album_with_artist_in_dir_name_with_one_song: service.OsWalkResult,
):
    songs = service.gather_songs(
        raw_artist_with_one_album_with_artist_in_dir_name_with_one_song
    )
    assert songs._songs[0].artist.name == "test artist"
    assert songs._songs[0].album.name == "test album"
    assert songs._songs[0].title == "First song"
    assert len(songs._songs) == 1
    assert not songs.is_empty()


@mark.unit
@mark.skip("Not implemented")
def test_gather_artist_with_one_album(
    raw_artist_with_one_album_with_one_song: service.OsWalkResult,
):
    songs = service.gather_songs(raw_artist_with_one_album_with_one_song)
    assert songs._songs[0].artist.name == "test artist"
    assert songs._songs[0].album.name == "test album"
    assert songs._songs[0].title == "First song"
    assert len(songs._songs) == 1
    assert not songs.is_empty()
