import os
import re
from pathlib import Path
from typing import List, Optional

from deflacue import deflacue  # type: ignore

from mptreasury.core import config, constants


class RawSong:
    def __init__(
        self,
        title: str,
        path: Path,
        album_name: str | None = None,
        artist_name: str | None = None,
    ):
        self.title = title
        self.album_name = album_name
        self.artist_name = artist_name
        self.path = path


class CueParser:
    def __init__(self, config: config.Config):
        # split the album file into song files
        self._config = config

    def parse_cue_file_data(self, cue_folder: Path):
        cue_files = [file for file in os.listdir(cue_folder) if file.endswith(".cue")]
        if len(cue_files) != 1:
            raise NotImplementedError("Cannot parse multiple cue files")
        cue_file = Path(cue_folder / cue_files[0])
        with cue_file.open("rb") as f:
            album_name = ""
            artist_name = ""
            details = ""
            # TODO: register a custom error handler for decoding: for example \x96 is almost like a dash, and should be replaced with dash
            # TODO: when a parsing error ocurred, we should also update the CUE file (or maybe deflacue should fix this?)
            while line := f.readline().decode(errors="ignore"):
                if line.startswith("TITLE"):
                    album_name = line.split(" ", 1)[1].replace("\n", "").strip('"')
                if line.startswith("PERFORMER"):
                    artist_name = line.split(" ", 1)[1].replace("\n", "").strip('"')
                if line.startswith("REM COMMENT"):
                    details = line.split(" ", 1)[1].replace("\n", "").strip('"')
        return album_name, artist_name, details

    def split_songs(self, cue_folder: Path, album_name: str, artist_name: str):
        # TODO: mb we should check that sox libsox-fmt-all are installed before trying anythin
        d = deflacue.Deflacue(cue_folder, dest_path=self._config.CACHE_FOLDER)
        d.do()
        partial_path = Path(self._config.CACHE_FOLDER / cue_folder.name)
        return self._get_folder_with_songs(partial_path)

    def _get_folder_with_songs(self, start_folder: Path):
        subfolders = []
        for res in os.listdir(start_folder):
            file = start_folder / res
            if file.suffix in constants.ALL_MUSIC_EXTENSIONS:
                return start_folder
            elif file.is_dir():
                subfolders.append(file)
        if len(subfolders) != 1:
            raise ValueError("Something is wrong with deflacue")
        return self._get_folder_with_songs(subfolders[0])


class RawAlbum:
    def __init__(self, music_path: Path, cue_parser: CueParser):
        self.music_path = music_path
        self.songs: List[RawSong] = []
        if self._is_cue_folder(self.music_path):
            self.name, self.artist_name, self.details = cue_parser.parse_cue_file_data(
                self.music_path
            )
            self.music_path = cue_parser.split_songs(
                self.music_path, self.name, self.artist_name
            )
        else:
            (
                self.name,
                self.artist_name,
                self.details,
            ) = self._get_data_from_album_folder_name(self.music_path.name)
        songs = self._gather_songs(self.music_path)
        for song in songs:
            song.album_name = self.name
            song.artist_name = self.artist_name
            self.songs.append(song)

    @staticmethod
    def _get_data_from_album_folder_name(folder_name: str):
        album_name = folder_name
        artist_name = ""
        details = ""
        # Usual details like year, label, edition can be found in parentheses
        if match := re.match(r".*?(\(.*\))", folder_name):
            details = match.groups()[0].strip()
            folder_name = folder_name.replace(details, "")
            # strip the parentheses
            details = details.strip("()").strip()
        # Usual details like year, label, edition can also be found in brackets
        # Based on some subjective observation, brackets tend to have more importance;
        # thus, they gain priority in setting details
        if match := re.match(r".*?(\[.*\])", folder_name):
            details = match.groups()[0].strip()
            folder_name = folder_name.replace(details, "")
            # strip the parentheses
            details = details.strip("[]").strip()
        # if there's a year in the name we want it removed
        folder_name = re.sub(r"\d\d\d\d", "", folder_name)
        if "-" in folder_name:
            name_parts = folder_name.split("-")
            # because of various adjustments, it's possible we left some separators with nothing in them
            name_parts = [part.strip() for part in name_parts if part.strip() != ""]
            # most likely, it's "artist - album"
            if len(name_parts) == 1:
                album_name = name_parts[0]
            elif len(name_parts) == 2:
                artist_name = name_parts[0].strip()
                album_name = name_parts[1].strip()
        return album_name, artist_name, details

    def _is_cue_folder(self, music_path: Path) -> bool:
        songs_count = 0
        has_cue = False
        for res in os.listdir(music_path):
            file = Path(res)
            if file.suffix == ".cue":
                has_cue = True
            elif file.suffix in constants.ALL_MUSIC_EXTENSIONS:
                songs_count += 1
        if has_cue and songs_count > 0:
            return True
        else:
            return False

    def _gather_songs(self, path: Path) -> list[RawSong]:
        raw_songs: list[RawSong] = []
        for res in os.listdir(path):
            file = Path(res)
            if file.suffix in constants.SUPPORTED_MUSIC_EXTENSIONS:
                song = RawSong(
                    title=self._parse_song_file_name(file),
                    path=path / file,
                )
                raw_songs.append(song)
            elif file.suffix in constants.ALL_MUSIC_EXTENSIONS:
                raise NotImplementedError(
                    f"Importing {file.suffix} files not implemented"
                )
        if len(raw_songs) == 0:
            raise ValueError("no valid songs in path")
        return raw_songs

    def _parse_song_file_name(self, song_file: Path) -> str:
        song_file_name = re.sub(r"^(\d+\w*[- ]*)", "", str(song_file))
        song_file_name = song_file_name.replace(song_file.suffix, "")
        return song_file_name

    def song_by_title(self, title: str):
        for song in self.songs:
            if song.title == title:
                return song


class Album:
    def __init__(
        self,
        name: str,
        genre: str,
        released: int,
        artist_id: int,
        artist_name: str,
        master_provider_id: int,
        master_name: str,
        provider_id: int,
        id: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.genre = genre
        self.released = released
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.master_provider_id = master_provider_id
        self.master_name = master_name
        self.provider_id = provider_id


class Artist:
    def __init__(self, id: int, name: str, provider_id: Optional[int] = None):
        self.id = id
        self.name = name
        self.provider_id = provider_id


class Song:
    title: str
    album_name: str

    def __init__(
        self,
        title: str,
        # track_number: int,
        # genre: str,
        # released: datetime.datetime,
        # album_id: int,
        album_name: str,
        # artist_id: int,
        artist_name: str,
        local_path: Path | None = None,
        remote_path: Path | None = None,
        album: Optional[Album] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.title = title
        # self.genre = genre
        # self.released = released
        """TODO: custom type that ensures
        - optionally, has a prefix"""
        if local_path:
            self.local_path = local_path
        if remote_path:
            self.remote_path = remote_path
        else:
            self.remote_path = None
        # self.album_id = album_id
        self.album_name = album_name
        # self.artist_id = artist_id
        self.artist_name = artist_name
        self.album = album

    def printable_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            album_name=self.album_name,
            artist_name=self.artist_name,
            path=str(self.local_path),
        )


UnknownArtist = Artist(id=-1, name="Unknown Artist")
