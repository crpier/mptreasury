import os
from pathlib import Path
import shutil
from pytest import mark, fixture
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app import db
from app.model import Album, Song

from app.service import import_songs


@fixture
def album_dir():
    album_dir_name = "Biglietto Per L'Inferno (SHM-CD)"
    song_names = [
        "01 - Ansia.flac",
        "02 - Confessione.flac",
        "03 - Una Strana Regina.flac",
        "04 - Il Nevare.flac",
        "05 - L'Amico Suicida.flac",
    ]
    music_path = Path(os.path.join(".", "testdata", album_dir_name))
    os.makedirs(music_path)
    for song_name in song_names:
        song_path = Path(music_path / song_name)
        song_path.touch()

    yield music_path.absolute()

    shutil.rmtree(music_path)


@fixture
def in_memory_engine():
    engine = create_engine("sqlite://")
    db.create_tables(engine)
    return engine


@fixture
def test_session(in_memory_engine):
    Session = sessionmaker(in_memory_engine)
    return Session


def album_exists(album_name: str, Session):
    with Session(future=True) as session:
        existing_album = session.execute(
            select(Album).filter_by(name=album_name)
        ).first()
        return bool(existing_album)


def song_exists(song_name: str, Session):
    with Session(future=True) as session:
        existing_album = session.execute(
            select(Song).filter_by(title=song_name)
        ).first()
        return bool(existing_album)


@mark.component
def test_import_new_album(album_dir: Path, test_session):
    import_songs(album_dir, test_session)

    assert album_exists("Biglietto Per L'Inferno", test_session)
    for song in [
        "Ansia",
        "Confessione",
        "Una Strana Regina",
        "Il Nevare",
        "L'Amico Suicida",
    ]:
        assert song_exists(song, test_session)
