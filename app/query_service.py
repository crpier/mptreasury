from app import db


def query_songs(query: str, Session):
    songs = [res[0] for res in db.get_songs(query, Session)]
    ids = [song.id for song in songs]
    songs_by_album = [res[0] for res in db.get_songs_by_album(query, Session)]
    for song in songs_by_album:
        if song.id not in ids:
            songs.append(song)
    return songs
