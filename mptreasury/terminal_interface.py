from pathlib import Path

import click

from mptreasury import bootstrap, import_service


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


def import_action(import_path: Path, upload_to_remote: bool = False):
    try:
        res = import_service.import_folder(
            music_path=import_path,
            config=config,
        )
    except ValueError as e:
        raise click.ClickException(str(e))
    # if res:
    #     _, songs = res
    #     if upload_to_remote:
    #         remote_storage_service.upload_local_songs(
    #             songs=songs,
    #             library_bucket=config.S3_LIBRARY_BUCKET,
    #             s3_client=s3_client,
    #         )


if __name__ == "__main__":
    main.add_command(import_dir, name="import")
    config = bootstrap.bootstrap()
    main()
