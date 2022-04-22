from pydantic import BaseSettings

class Settings(BaseSettings):
    DISCOGS_PAT: str
