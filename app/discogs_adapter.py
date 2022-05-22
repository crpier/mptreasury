from typing import List, Tuple

import discogs_client.models as discogs_models
from fuzzywuzzy import fuzz

from app.model import Album, RawAlbum, Song


# TODO: this is quite the convoluted piece of logic. unit test it I guess 🤷
def fuzzy_match_tracks(actual_tracks: List[str], potential_matches: List[str]):
    # Triplets of actual track, potential match, matching score
    # Could this be dog 🤔
    triplets: List[Tuple[str, str, int]] = []
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
    triplets: List[Tuple[str, str, int]],
    no_of_actual_tracks: int,
    no_of_potential_tracks: int,
):
    score_sum = sum([triplet[2] for triplet in triplets])
    score_mean = score_sum / len(triplets)
    score_mean = score_mean * (1 - 0.2 * no_of_actual_tracks)
    potential_tracks_diff = no_of_potential_tracks - len(triplets)
    score_mean = score_mean * (1 - 0.2 * potential_tracks_diff)
    return score_mean


class FakeTrack:
    def __init__(self, title) -> None:
        self.title = title


class FakeArtist:
    id = 1234
    name = "test artist"


class FakeMaster:
    title = "test master"
    id = 12345


class FakeDiscogsAlbum:
    def __init__(self, track_names: List[str]) -> None:
        self.tracklist = [FakeTrack(title) for title in track_names]
        self.title = "test album"
        self.genres = ["test genre 1", "test genre 2"]
        self.year = 1986
        self.artists = [FakeArtist()]
        self.id = 123
        self.master = FakeMaster()


class PaginatedList:
    def __init__(self, tracks: List[str]) -> None:
        self._tracks = tracks

    def page(self, _):
        return [FakeDiscogsAlbum(self._tracks)]


class FakeDiscogsClient:
    """Discogs client that will not actually contact the discogs server
    but will implements the real client's interface:
    has a .search() method, that will return a paginated list,
        that will return a list of albums, that has a .tracklist() list of tracks
        that have a .title attribute
    tracklist: the list of titles that the tracks should have
    """

    def __init__(self, tracklist: List[str]) -> None:
        self._tracklist = tracklist

    def search(self, *args, **kwargs):
        return PaginatedList(self._tracklist)


class DiscogsAdapter:
    def __init__(self, client):
        self._client = client

    def populate_raw_album(self, raw_album: RawAlbum, max_attempts=3):
        match_triplets = None
        paginated_list = self._client.search(
            raw_album.name, type="release", artist_name=raw_album.artist_name
        )
        # We never really want to go to the second page, it's quite unlikely we'll encounter that many albums
        result_albums: List[discogs_models.Release] = paginated_list.page(1)
        for _, album_res in zip(range(max_attempts), result_albums):
            discogs_tracks = [track.title for track in album_res.tracklist]  # type: ignore
            match_triplets, overall_score = fuzzy_match_tracks(
                raw_album.track_names.copy(), discogs_tracks
            )
            if overall_score < 80:
                # TODO: actually, ask the user
                continue
            new_songs: List[Song] = []
            new_album = Album(
                name=album_res.title,  # type: ignore
                genre=album_res.genres[0],  # type: ignore
                released=album_res.year,  # type: ignore
                artist_id=album_res.artists[0].id,  # type: ignore # type: ignore
                artist_name=album_res.artists[0].name,  # type: ignore
                provider_id=album_res.id,  # type: ignore
                master_name=album_res.master.title,  # type: ignore
                master_provider_id=album_res.master.id,  # type: ignore
            )
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

            return new_songs, new_album
        raise ValueError("could not populate album")
