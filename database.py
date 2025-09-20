"""Database engine/session setup and lightweight migrations.

Creates the SQLAlchemy engine and session factory and provides `init_db()` to
create tables. Also includes a safe, best-effort auto-migration to ensure the
optional `qa` column exists in `interview_questions`.
"""

from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import settings


class Base(DeclarativeBase):
    """Base class for ORM models."""
    pass


# Create engine; pool_pre_ping helps avoid stale connections for MySQL
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # avoid stale MySQL connections
    future=True,
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def init_db() -> None:
    """Import models and create tables if they don't exist."""
    # Import models here to ensure they are registered with Base.metadata
    from models import InterviewQuestion  # noqa: F401

    # Create ORM-declared tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Lightweight, safe migration: ensure optional columns exist
    try:
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("interview_questions")}
        if "qa" not in columns:
            # MySQL-compatible ALTER to add nullable TEXT column after questions
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE interview_questions ADD COLUMN qa TEXT NULL AFTER questions"))
    except Exception:
        # Don't block app startup if inspection or migration fails.
        # A clearer DB error will surface on insert. This is intentionally silent to avoid
        # breaking environments without permissions for ALTER TABLE.
        pass


@contextmanager
def get_session():
    """Provide a transactional session scope.

    Usage:
        with get_session() as session:
            ... use session ...
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
