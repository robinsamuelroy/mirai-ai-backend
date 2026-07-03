# src/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # tests connection before using it — prevents stale connection errors
)

SessionLocal = sessionmaker(
    autocommit=False,   # we control when to commit — safer
    autoflush=False,    # don't auto-save until we say so
    bind=engine,
)

Base = declarative_base()  # all your models will inherit from this


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db        # hand the session to the route function
    finally:
        db.close()      # always runs, even on exceptions