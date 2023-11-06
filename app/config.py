from enum import Enum
from pathlib import Path


class APP_ENV(str, Enum):
    production = "production"
    dev = "dev"


class Config():
    # TODO: validate paths
    LIBRARY_DIR: Path = Path("./lib")
    DISCOGS_PAT: str = "aa"
    APP_ENV: str = "prod"
    # TODO: can I remove this from initial declaration?
    DB_FILE: Path = Path("dev.db")
    CACHE_FOLDER: Path = Path("~/.cache/mptreasury").expanduser()
    S3_LIBRARY_BUCKET: str | None = None
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
