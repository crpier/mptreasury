import logging
import unicodedata
from pathlib import Path

from app import config, model

logger = logging.getLogger("mptreasury")


def upload_local_songs(songs: list[model.Song], library_bucket: str, s3_client):
    for song in songs:
        if not song.local_path:
            raise ValueError(f"Song {song.title} does not exist locally; cannot upload")
        if song.remote_path:
            raise ValueError(
                f"Song {song.title} has already been uploaded; cannot upload again - you should copy or move its remote location"
            )

        song.remote_path = Path(
            unicodedata.normalize(
                "NFKD",
                f"{song.artist_name}/{song.album_name}/{song.title}{song.local_path.suffix}",
            )
            .encode("ascii", "ignore")
            .decode()
        )
        # TODO: we should check for the path, or for the songs being there already
        
        logger.info("Uploading %s to %s", song.title, song.remote_path)
        s3_client.upload_file(
            str(song.local_path), library_bucket, str(song.remote_path)
        )
