from discogs_client import Client
from sqlalchemy.orm import Session

from mptreasury.adapters.discogs_adapter import Searcher
from mptreasury.core.config import Config
from mptreasury.core.db import get_sessionmaker, create_tables
from mptreasury.util.injection import add_injectable


def bootstrap():
    config = Config()
    add_injectable(Config, config)

    session = get_sessionmaker(config)
    create_tables()
    add_injectable(Session, session)

    client = Client("mptreasury/0.1", user_token=config.DISCOGS_PAT)
    # add_injectable(Client, client)

    searcher = Searcher(client)
    add_injectable(Searcher, searcher)
