"""Database engine configuration with enterprise connection pooling."""
from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings

logger = logging.getLogger("aerosense.db")

settings = get_settings()
DATABASE_URL = settings.database_url

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
_engine_kwargs: dict = {"connect_args": _connect_args}

if DATABASE_URL == "sqlite:///:memory:":
    _engine_kwargs["poolclass"] = StaticPool
elif not DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update({
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_pre_ping": True,
        "pool_recycle": settings.db_pool_recycle,
    })

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""

    pass


def init_db() -> None:
    """Initialize database tables and check for persistent volume mount safety."""
    from app import models  # noqa: F401

    if settings.environment == "production" and DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        is_mounted = any(db_path.startswith(p) for p in ("/data", "/mnt", "/var/lib", "C:\\data"))
        if not is_mounted:
            logger.warning(
                "OPERATIONAL RISK NOTICE: Running file-based SQLite in production container without a persistent volume mount. "
                "For high-availability production, configure PostgreSQL or mount a persistent volume at /data."
            )

    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """Provide a transactional SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
