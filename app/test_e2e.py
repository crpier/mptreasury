import os
import re
import shutil
from pathlib import Path
from typing import List

import pytest
from mutagen.easyid3 import EasyID3

from app import discogs_adapter, service, test_utils
from app.conftest import memory_session
from app.model import Song


@pytest.fixture
def basic_song_list():
    songs: List[Song] = []
    for i in range(6):
        new_song = test_utils.make_test_mp3(
            title=f"Title {i}", file_name_without_extension=f"{i} - Title {i}"
        )
        songs.append(new_song)

    yield songs

    for song in songs:
        try:
            test_utils.clean_test_mp3(song)
        except FileNotFoundError:
            pass


@pytest.fixture
def src_and_dest_folders():
    music_path = Path("testdata")
    dest_folder = music_path / "dest"
    os.makedirs(dest_folder)
    yield music_path, dest_folder

    shutil.rmtree(dest_folder)


@pytest.mark.e2e
def test_import_e2e(basic_song_list: List[Song], memory_session, src_and_dest_folders):
    music_path, dest_folder = src_and_dest_folders
    tracklist = [song.title for song in basic_song_list]
    file_names = [os.path.basename(song.path) for song in basic_song_list]
    fake_client = discogs_adapter.FakeDiscogsClient(tracklist)
    fake_metadata_retriever = discogs_adapter.DiscogsAdapter(fake_client)
    service.import_songs(
        music_path=music_path,
        root_music_path=dest_folder,
        Session=memory_session,
        metadata_retriever=fake_metadata_retriever,
    )
    song_file_names = []
    for song_path_name in os.listdir(dest_folder / "test artist" / "test album"):
        song_path = Path(dest_folder / "test artist" / "test album" / song_path_name)
        song_file_names.append(os.path.basename(song_path))

        imported_song = EasyID3(song_path)
        assert re.match(
            r"^Title \d", imported_song["title"][0]
        ), f"Title {imported_song['title'][0]} is incorrect"
        assert imported_song["album"][0] == "test album"
        assert imported_song["artist"][0] == "test artist"

    assert sorted(song_file_names) == sorted(
        file_names
    ), "Input song list was changed when importing songs"
