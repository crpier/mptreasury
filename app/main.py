import sys
from pathlib import Path

import discogs_client

import app.db
import app.model
import app.service
from app import discogs_adapter
from app.config import config


def main(music_path: Path, dest_path: Path):
    session = app.db.sessionmaker(app.db.engine)
    app.db.create_tables(app.db.engine)
    print("started!!!")

    client = discogs_client.Client("mptreasury/0.1", user_token=config.DISCOGS_PAT)
    metadata_retriever = discogs_adapter.DiscogsAdapter(client)

    app.service.import_songs(
        music_path,
        session,
        dest_path,
        metadata_retriever,
    )


if __name__ == "__main__":
    music_path = Path(sys.argv[1])
    dest_path = Path(sys.argv[2])
    main(music_path, dest_path)
