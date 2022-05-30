from pathlib import Path
import click

import discogs_client

from app import db
from app import import_service
from app import query_service
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
@click.option(
    "--fields",
    default="",
    help="List of fields to show. Example with all available: "
    "'title,path,album_name,artist_name,id'",
)
def query_songs(query: str, fields: str):
    if query == "":
        click.Abort("Query cannot be empty!")
    if query.encode("ascii"):
        click.Abort("UTF8 queries not implemented 😔")
    properties_to_show = fields.split(",")
    songs = query_service.query_songs(query, session)
    for song in songs:
        song = song.printable_dict()
        if not fields:
            click.echo(f"{song['title']} - {song['album_name']}")
        else:
            representation = {
                property: song[property] for property in properties_to_show
            }
            click.echo(representation)


def import_action(import_path: Path):
    client = discogs_client.Client("mptreasury/0.1", user_token=settings.DISCOGS_PAT)
    metadata_retriever = discogs_adapter.DiscogsAdapter(client)

    import_service.import_songs(
        music_path=import_path,
        Session=session,
        root_music_path=dest_path,
        metadata_retriever=metadata_retriever,
    )


if __name__ == "__main__":
    main.add_command(import_dir)
    main.add_command(query_songs)
    settings = bootstrap.bootstrap()
    dest_path = settings.LIBRARY_DIR
    session = db.get_sessionmaker(settings)
    db.create_tables()

    main()
