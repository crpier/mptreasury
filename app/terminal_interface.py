from pathlib import Path

import boto3
import click
import discogs_client

from app import (
    bootstrap,
    db,
    discogs_adapter,
    import_service,
    remote_storage_service,
)


@click.group()
def main():
    pass


@click.command()
@click.option(
    "--music-dir",
    help="An album folder (a folder with songs from one album in it) or an artist folder(a folder with album folders in it)",
)
@click.option(
    "--upload-to-remote",
    help="Whether to also upload imported music to the remote storage",
    default=False,
)
def import_dir(music_dir: str, upload_to_remote: bool):
    if music_dir is None:
        click.echo("dude wtf")
        raise click.ClickException("Why no music dir?")
    music_path = Path(music_dir)
    # TODO: move these validations at service level
    if not music_path.exists():
        click.echo(f"Given target {music_dir} does not exist!")
        click.Abort()
    if not music_path.is_dir():
        click.echo(f"Given target {music_dir} is not a folder!")
        click.Abort()
    music_path = music_path.absolute()
    import_action(import_path=music_path, upload_to_remote=upload_to_remote)


# @click.command()
# @click.option("--query", help="Text query to issue")
# @click.option(
#     "--fields",
#     default="",
#     help="List of fields to show. Example with all available: "
#     "'title,path,album_name,artist_name,id'",
# )
# def query_songs(query: str, fields: str):
#     if query == "":
#         click.Abort("Query cannot be empty!")
#     if query.encode("ascii"):
#         click.Abort("UTF8 queries not implemented 😔")
#     properties_to_show = fields.split(",")
#     songs = query_service.query_songs(query, session)
#     for song in songs:
#         song = song.printable_dict()
#         if not fields:
#             click.echo(f"{song['title']} - {song['album_name']}")
#         else:
#             representation = {
#                 property: song[property] for property in properties_to_show
#             }
#             click.echo(representation)


def import_action(import_path: Path, upload_to_remote: bool):
    client = discogs_client.Client("mptreasury/0.1", user_token=settings.DISCOGS_PAT)
    discogs_searcher = discogs_adapter.discogsLookupFactory(client)

    try:
        res = import_service.import_folder(
            music_path=import_path,
            Session=session,
            root_music_path=dest_path,
            searcher=discogs_searcher,
            config=settings,
        )
    except ValueError as e:
        raise click.ClickException(str(e))
    if res:
        _, songs = res
        if upload_to_remote:
            remote_storage_service.upload_local_songs(
                songs=songs, library_bucket=settings.S3_LIBRARY_BUCKET, s3_client=s3_client
            )


if __name__ == "__main__":
    main.add_command(import_dir)
    # main.add_command(query_songs)
    settings = bootstrap.bootstrap()
    dest_path = settings.LIBRARY_DIR
    session = db.get_sessionmaker(settings)
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )
    if not s3.meta:
        raise ConnectionError("Cannot instantiate S3 client")
    s3_client = s3.meta.client

    db.create_tables()

    main()
