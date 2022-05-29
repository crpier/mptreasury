from pathlib import Path
import click

import discogs_client

from app import db
import app.model
import app.import_service
from app import discogs_adapter
from app import bootstrap


@click.group()
def main():
    pass


@click.command()
@click.option("--music_dir", help="Add new music to the library")
def import_dir(music_dir: str):
    if music_dir is not None:
        music_path = Path(music_dir)
        if not music_path.exists():
            click.echo(f"Given target {music_dir} does not exist!")
            click.Abort()
        if not music_path.is_dir():
            click.echo(f"Given target {music_dir} is not a folder!")
            click.Abort()
        music_path = music_path.absolute()
        import_action(import_path=music_path)


@click.command()
@click.option("--query", help="Text query to issue")
def query_songs(query: str):
    pass


def import_action(import_path: Path):
    settings = bootstrap.bootstrap()
    dest_path = settings.LIBRARY_DIR
    session = db.get_sessionmaker(settings)
    db.create_tables()

    client = discogs_client.Client("mptreasury/0.1", user_token=settings.DISCOGS_PAT)
    metadata_retriever = discogs_adapter.DiscogsAdapter(client)

    app.import_service.import_songs(
        music_path=import_path,
        Session=session,
        root_music_path=dest_path,
        metadata_retriever=metadata_retriever,
    )


if __name__ == "__main__":
    main.add_command(import_dir)
    main.add_command(query_songs)
    main()
