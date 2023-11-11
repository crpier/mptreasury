import os
from pathlib import Path
from typing import Any, Literal, TypeVar, final

ENV = Literal["prod", "dev", "unit-test", "acceptance-test"]

T = TypeVar("T")


def from_env_or_from_var(type: Any, env_name: str, var: T) -> T:
    if value := os.getenv(env_name, None):
        return type(value)
    return var


@final
class Config:
    __slots__ = (
        "LIBRARY_DIR",
        "DISCOGS_PAT",
        "APP_ENV",
        "DB_FILE",
        "CACHE_FOLDER",
        "S3_LIBRARY_BUCKET",
        "AWS_ACCESS_KEY",
        "AWS_SECRET_KEY",
        "SOCKET_PATH",
    )

    def __init__(
        self,
        LIBRARY_DIR: Path = Path("./lib"),
        DISCOGS_PAT: str = "aa",
        APP_ENV: ENV = "dev",
        DB_FILE: Path = Path("dev.db"),
        CACHE_FOLDER: Path = Path("~/.cache/mptreasury").expanduser(),
        S3_LIBRARY_BUCKET: str | None = None,
        AWS_ACCESS_KEY: str | None = None,
        AWS_SECRET_KEY: str | None = None,
        SOCKET_PATH: Path = Path("/tmp/my_socket"),
    ) -> None:
        self.LIBRARY_DIR = from_env_or_from_var(Path, "LIBRARY_DIR", LIBRARY_DIR)
        self.DISCOGS_PAT = from_env_or_from_var(str, "DISCOGS_PAT", DISCOGS_PAT)
        self.APP_ENV = from_env_or_from_var(ENV, "APP_ENV", APP_ENV)
        self.DB_FILE = from_env_or_from_var(Path, "DB_FILE", DB_FILE)
        self.CACHE_FOLDER = from_env_or_from_var(Path, "CACHE_FOLDER", CACHE_FOLDER)
        self.S3_LIBRARY_BUCKET = from_env_or_from_var(
            str, "S3_LIBRARY_BUCKET", S3_LIBRARY_BUCKET
        )
        self.AWS_ACCESS_KEY = from_env_or_from_var(
            str, "AWS_ACCESS_KEY", AWS_ACCESS_KEY
        )
        self.AWS_SECRET_KEY = from_env_or_from_var(
            str, "AWS_SECRET_KEY", AWS_SECRET_KEY
        )
        self.SOCKET_PATH = from_env_or_from_var(Path, "SOCKET_PATH", SOCKET_PATH)

    def db_uri(self):
        return f"sqlite:///{self.DB_FILE}"
