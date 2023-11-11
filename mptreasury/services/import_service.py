import os
import shutil
import typing
import unicodedata
from enum import StrEnum
from pathlib import Path

from discogs_client import models as discogs_models
from fuzzywuzzy import fuzz  # type: ignore
from loguru import logger
from sqlalchemy.orm import Session

from app.model import Album, CueParser, RawAlbum, Song
from mptreasury.adapters.discogs_adapter import Searcher
from mptreasury.core import constants, db
from mptreasury.core.config import Config
from mptreasury.util.injection import Injected, injectable_sync


class FolderType(StrEnum):
    album_folder = "album_folder"
    artist_folder = "artist_folder"


def determine_folder_type(path: Path) -> FolderType:
    subdirs = 0
    music_files = 0
    has_cue = False
    for result in os.listdir(path):
        item = Path(result)
        if item.suffix == ".cue":
            has_cue = True
        if item.is_dir():
            subdirs += 1
        else:
            if item.suffix in constants.ALL_MUSIC_EXTENSIONS:
                music_files += 1
    if has_cue and music_files == 1:
        return FolderType.album_folder
    elif music_files > subdirs:
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
        normalized_song_file_name = (
            unicodedata.normalize("NFKD", f"{song.title}{song.local_path.suffix}")
            .encode("ascii", "ignore")
            .decode()
        )

        if not target_folder_path.exists():
            os.makedirs(target_folder_path)
        target_path = target_folder_path / normalized_song_file_name
        shutil.copy(song.local_path, target_path)
        song.local_path = target_path


# TODO: this is quite the convoluted piece of logic. do some renames and add a dataclass for these triplets maybe?
def fuzzy_match_tracks(actual_tracks: list[str], potential_matches: list[str]):
    # Triplets of actual track, potential match, matching score
    # Could this be dog 🤔

    # create a copy of the list so that we can change it safely
    actual_tracks = actual_tracks.copy()
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


@injectable_sync
def load_discogs_album_into_raw_album(
    album_res: discogs_models.Release,
    raw_album: RawAlbum,
    match_triplets: typing.Any,
    *,
    session: Session = Injected,
    config: Config = Injected,
):
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
    logger.info("Loading songs from {}", raw_album.songs[0].path.parent)
    for actual_track, potential_track, _ in match_triplets:
        raw_song = raw_album.song_by_title(actual_track)
        if not raw_song:
            raise ValueError("weird, a song from the raw album disappeared")
        new_song = Song(
            title=potential_track,
            local_path=raw_song.path,
            album_name=album_res.title,  # type: ignore
            artist_name=album_res.artists[0].name,  # type: ignore
            album=new_album,
        )
        new_songs.append(new_song)
    if not (id := db.get_album_id(new_album, session)):
        logger.info("Adding songs for {} to library", new_album.name)
        copy_songs_to_music_folder(new_songs, config.LIBRARY_DIR)
        db.add_album_and_songs(new_album, new_songs, session)
    else:
        logger.info("Album {} already in db with id: {}", new_album.name, id)
    return new_album, new_songs


@injectable_sync
def import_folder(
    music_path: Path,
    *,
    config: Config = Injected,
    searcher: Searcher = Injected,
    Session: Session = Injected,
):
    music_path = music_path.expanduser()
    logger.info("Gonna look up in {}", music_path)
    folder_type = determine_folder_type(music_path)
    match folder_type:
        case FolderType.album_folder:
            raw_albums = [RawAlbum(music_path, cue_parser=CueParser(config))]
        case FolderType.artist_folder:
            raw_albums = []
            for res in os.listdir(music_path):
                album_path = music_path / res
                raw_albums.append(RawAlbum(album_path, cue_parser=CueParser(config)))

    for raw_album in raw_albums:
        raw_tracks = [track.title for track in raw_album.songs]
        raw_tracks.sort()
        logger.info(
            "Trying to import {} by {} from {}",
            raw_album.name,
            raw_album.artist_name,
            raw_album.music_path,
        )
        logger.info(
            "Searching for album {} from {}", raw_album.name, raw_album.artist_name
        )
        search = searcher.search(
            album_name=raw_album.name,
            artist_name=raw_album.artist_name,
        )
        candidates = search.next_page()
        for i, album_res in zip(range(constants.MAX_GUESS_ATTEMPTS), candidates):
            discogs_tracks = [track.title for track in album_res.tracklist if track.fetch("type_") == "track"]  # type: ignore
            discogs_tracks.sort()
            match_triplets, overall_score = fuzzy_match_tracks(
                raw_tracks, discogs_tracks
            )
            if overall_score >= constants.MINIMUM_MATCHING_ALBUM_SCORE:
                logger.info("Accepted candidate {}: {} by {} - {} with score {}", i, album_res.title, album_res.artists[0].name, album_res.id, overall_score)  # type: ignore
                logger.info(
                    "Attempting to import tracks: {}",
                    raw_tracks,
                )
                logger.info("Accepted candidate tracks: {}", discogs_tracks)
                album, songs = load_discogs_album_into_raw_album(
                    album_res=album_res,
                    raw_album=raw_album,
                    match_triplets=match_triplets,
                    session=Session,
                )
                return album, songs
            else:
                logger.info("Rejected candidate {}: {} by {} - {} with score {}", i, album_res.title, album_res.artists[0].name, album_res.id, overall_score)  # type: ignore
        logger.info("No matching condidate was worthy. Exiting")
