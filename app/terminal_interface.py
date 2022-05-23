from pathlib import Path
import click

import discogs_client

from app import db
import app.model
import app.service
from app import discogs_adapter
from app import bootstrap


@click.command()
@click.argument("target_dir")
def main(target_dir: str):
    settings = bootstrap.bootstrap()
    click.echo(settings)
    dest_path = settings.LIBRARY_DIR
    music_path = Path(target_dir)
    if not music_path.exists():
        click.echo(f"Given target {target_dir} does not exist!")
        click.Abort()
    if not music_path.is_dir():
        click.echo(f"Given target {target_dir} is not a folder!")
        click.Abort()
    music_path = music_path.absolute()
    session = db.get_sessionmaker(settings)
    db.create_tables()

    client = discogs_client.Client("mptreasury/0.1", user_token=settings.DISCOGS_PAT)
    metadata_retriever = discogs_adapter.DiscogsAdapter(client)

    app.service.import_songs(
        music_path=music_path,
        Session=session,
        root_music_path=dest_path,
        metadata_retriever=metadata_retriever,
    )


if __name__ == "__main__":
    main()
