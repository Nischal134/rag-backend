# app/db/session.py

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# The engine is the actual connection to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # drops stale connections automatically
    pool_size=10,
    max_overflow=20,
)

# A factory that produces database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI will call this as a dependency.
    It opens a session, hands it to your route function,
    and guarantees it gets closed afterwards — even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()