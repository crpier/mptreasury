from enum import Enum
from pathlib import Path
from typing import Optional, Any

from pydantic import BaseSettings
from pydantic.typing import StrPath


class APP_ENV(str, Enum):
    production = "production"
    dev = "dev"


class Config(BaseSettings):
    #TODO: validate paths
    LIBRARY_DIR: Path
    DISCOGS_PAT: str
    DB_FILE: Optional[Path]
    # TODO: figure out why pydantic breaks when I use an enum with default value
    # APP_ENV: APP_ENV = APP_ENV.production
    APP_ENV: str = "prod"
    DB_URI: str = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.DB_FILE:
            db_file = self.DB_FILE.absolute()
        else:
            db_file = ""
        self.DB_URI = f"sqlite:///{db_file}"
