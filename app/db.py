from sqlmodel import SQLModel, create_engine

from app.config import config

engine = create_engine(config.DB_URI, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

