import logging
from pathlib import Path

import pytest

from app import model, remote_storage_service

# TODO: isn't there a better place for this?
logger = logging.getLogger("mptreasury")
logger.setLevel(logging.WARNING)


class FakeS3Client:
    def __init__(self) -> None:
        self.calls = []

    def upload_file(self, local_path: str, library_bucket: str, remote_path: str):
        self.calls.append((local_path, library_bucket, remote_path))


@pytest.fixture
def fake_s3_client() -> FakeS3Client:
    return FakeS3Client()


@pytest.fixture
def song_with_remote_path() -> model.Song:
    return model.Song(
        title="Test Title",
        album_name="Test Album",
        artist_name="Test Artist",
        local_path=Path("test"),
        remote_path=Path("test"),
    )


def test_song_with_remote_path_is_not_uploaded(
    song_with_remote_path: model.Song, fake_s3_client: FakeS3Client
):
    """Test that when a song already has a remote an exception is raised,
    instead of trying to upload it"""
    with pytest.raises(ValueError):
        remote_storage_service.upload_local_songs(
            [song_with_remote_path], library_bucket="aaa", s3_client=fake_s3_client
        )


@pytest.fixture
def song_with_non_ascii_chars():
    return model.Song(
        title="Â Ê Title",
        album_name="Î Ô Test Album",
        artist_name="Û Ŝ Test Artist",
        local_path=Path("test"),
    )


def test_remote_path_is_normalized(
    song_with_non_ascii_chars: model.Song, fake_s3_client: FakeS3Client
):
    """Test that when a song's title, album and artist contain non-ASCII chars,
    they are normalized and replaced with similar ASCII chars"""
    remote_storage_service.upload_local_songs(
        [song_with_non_ascii_chars], library_bucket="aaa", s3_client=fake_s3_client
    )
    assert fake_s3_client.calls == [
        ("test", "aaa", "U S Test Artist/I O Test Album/A E Title")
    ]
