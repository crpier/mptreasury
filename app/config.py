from enum import Enum

from pydantic import BaseSettings


class APP_ENV(str, Enum):
    production = "production"
    dev = "dev"


class Config(BaseSettings):
    DISCOGS_PAT: str
    # TODO:custom type or smth i think??
    DB_URI: str
    # TODO: figure out why pydantic breaks when I use an enum with default value
    # APP_ENV: APP_ENV = APP_ENV.production
    APP_ENV: str = "production"


config = Config()  # type: ignore
