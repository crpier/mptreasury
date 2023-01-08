from enum import Enum
import os
import re
import shutil
from pathlib import Path
import unicodedata

from app import db, discogs_adapter
from app.model import CueParser, RawAlbum, RawSong, Album, Song
from app import constants
from app import config


from fuzzywuzzy import fuzz  # type: ignore

import logging

logger = logging.getLogger("mptreasury")


class FolderType(str, Enum):
    album_folder = "album_folder"
    artist_folder = "artist_folder"


def determine_folder_type(path: Path) -> FolderType:
    subdirs = 0
    music_files = 0
    for result in os.listdir(path):
        item = Path(result)
        if item.is_dir():
            subdirs += 1
        else:
            if item.suffix in constants.ALL_MUSIC_EXTENSIONS:
                music_files += 1
    if music_files > subdirs:
        return FolderType.album_folder
    else:
        return FolderType.artist_folder


def copy_songs_to_music_folder(songs: list[Song], library_folder: Path):
    for song in songs:
        target_folder_name = os.path.join(
            library_folder, song.artist_name, song.album_name
        )
        normalized_target_folder_name = (
            unicodedata.normalize("NFKD", target_folder_name)
            .encode("ascii", "ignore")
            .decode()
        )
        target_folder_path = Path(normalized_target_folder_name)

        if not target_folder_path.exists():
            os.makedirs(target_folder_path)
        target_path = target_folder_path / f"{song.title}{song.path.suffix}"
        shutil.copy(song.path, target_path)


def validate_music_path(music_path: Path):
    assert music_path.exists()
    assert music_path.is_dir()


def parse_folder_name(path: str) -> dict[str, str]:
    # Order matters: the first one found is the first one used
    validator_regexes = [
        (r"^(.+)\(.+\)$", ("album",)),
        (r"^([A-z0-9 ]+).*?(\d+).*?([A-z0-9 ]+)$", ("artist", "year", "album")),
        (r"^(.+)$", ("album",)),
    ]
    validator: tuple[str, tuple]
    for validator in validator_regexes:
        match = re.search(validator[0], path)
        if match:
            results = {}
            for name, value in zip(validator[1], match.groups()):
                results[name] = value.strip()
            return results
    raise ValueError("Unrecognizable folder name")


# TODO: this is quite the convoluted piece of logic. do some renames and add a dataclass for these triplets maybe?
def fuzzy_match_tracks(actual_tracks: list[str], potential_matches: list[str]):
    # Triplets of actual track, potential match, matching score
    # Could this be dog 🤔
    triplets: list[tuple[str, str, int]] = []
    for potential_match in potential_matches:
        if len(actual_tracks) == 0:
            break
        scores = [
            fuzz.partial_ratio(potential_match, actual_track)
            for actual_track in actual_tracks
        ]
        index_max = max(range(len(scores)), key=scores.__getitem__)
        triplets.append((actual_tracks[index_max], potential_match, scores[index_max]))
        del actual_tracks[index_max]
    score = score_fuzzy_match_triplet(
        triplets, len(actual_tracks), len(potential_matches)
    )
    return triplets, score


def score_fuzzy_match_triplet(
    triplets: list[tuple[str, str, int]],
    no_of_actual_tracks: int,
    no_of_potential_tracks: int,
):
    score_sum = sum([triplet[2] for triplet in triplets])
    score_mean = score_sum / len(triplets)
    score_mean = score_mean * (1 - 0.2 * no_of_actual_tracks)
    potential_tracks_diff = no_of_potential_tracks - len(triplets)
    score_mean = score_mean * (1 - 0.2 * potential_tracks_diff)
    return score_mean


def import_folder(
    music_path: Path,
    Session,
    root_music_path: Path,
    searcher: type[discogs_adapter.Searcher],
    config: config.Config,
):
    logger.info("Gonna look up in %s", music_path)
    folder_type = determine_folder_type(music_path)
    match folder_type:
        case FolderType.album_folder:
            raw_albums = [RawAlbum(music_path, cue_parser=CueParser(config))]
        case FolderType.artist_folder:
            raise NotImplementedError("Importing multiple albums not implemented")
    for raw_album in raw_albums:
        logger.info("Trying to import %s by %s", raw_album.name, raw_album.artist_name)
        search = searcher(
            album_name=raw_album.name,
            artist_name=raw_album.artist_name,
        )
        candidates = search.next_page()
        for i, album_res in zip(range(constants.MAX_GUESS_ATTEMPTS), candidates):
            discogs_tracks = [track.title for track in album_res.tracklist if track.fetch("type_") == "track"]  # type: ignore
            match_triplets, overall_score = fuzzy_match_tracks(
                [track.title for track in raw_album.songs], discogs_tracks
            )
            logger.info("Candidate %s: %s by %s - %s with score %s", i, album_res.title, album_res.artists[0].name, album_res.id, overall_score)  # type: ignore
            if overall_score >= 81:
                new_songs: list[Song] = []
                new_album = Album(
                    name=str(album_res.title),
                    genre=album_res.genres[0],  # type: ignore
                    released=album_res.year,  # type: ignore
                    artist_id=album_res.artists[0].id,  # type: ignore # type: ignore
                    artist_name=album_res.artists[0].name,  # type: ignore
                    provider_id=album_res.id,  # type: ignore
                    master_name=album_res.master.title,  # type: ignore
                    master_provider_id=album_res.master.id,  # type: ignore
                )
                logger.info("Loading songs from %s", raw_album.songs[0].path.parent)
                for actual_track, potential_track, _ in match_triplets:
                    raw_song = raw_album.song_by_title(actual_track)
                    if not raw_song:
                        raise ValueError("weird, a song from the raw album disappeared")
                    new_song = Song(
                        title=potential_track,
                        path=raw_song.path,
                        album_name=album_res.title,  # type: ignore
                        artist_name=album_res.artists[0].name,  # type: ignore
                        album=new_album,
                    )
                    new_songs.append(new_song)
                if not (id := db.get_album_id(new_album, Session)):
                    logger.info("Adding songs for %s to library", new_album.name)
                    copy_songs_to_music_folder(new_songs, root_music_path)
                    db.add_album_and_songs(new_album, new_songs, Session)
                else:
                    logger.info(
                        "Album %s already in db with id: %s", new_album.name, id
                    )
                break
