import mutagen.easyid3

from app.model import Song


def update_metadata(song: Song):
    """Update metadata of the song file to match what's in the db"""
    tags = mutagen.easyid3.EasyID3(str(song.local_path))
    tags["title"] = song.title
    tags["artist"] = song.artist_name
    tags["album"] = song.album_name
    tags.save()
