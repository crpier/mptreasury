from app import db

def query_songs(query: str, Session):
    res = db.get_songs(query, Session)
    res = res + db.get_songs_by_album(query, Session)
    # this removes duplicates
    res = list(set(res))
    return res
