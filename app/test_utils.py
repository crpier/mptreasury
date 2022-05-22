import os
import subprocess
from pathlib import Path

from app import metadata_adapter
from app.model import Song


def _generate_silent_song(song: Song):
    res = subprocess.run(
        f"ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 5 '{song.path}'",
        shell=True,
    )
    metadata_adapter.update_metadata(song)
    print(res)


def make_test_mp3(title="test_title", file_name_without_extension="0 - test song"):
    song = Song(
        title=title,
        album_name="test_album",
        artist_name="test_artist",
        path=Path(f"testdata/{file_name_without_extension}.mp3"),
        album=None,
    )
    _generate_silent_song(song)
    return song


def clean_test_mp3(song: Song):
    os.remove(song.path)
