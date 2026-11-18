"""FastAPI dependency injection utilities for database sessions, authentication, and LLM providers."""
from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions import SecurityValidationError
from app.llm.provider import LLMProvider, get_llm_provider
from app.security import verify_session_token


def get_current_session_id(
    authorization: Annotated[str | None, Header(description="Bearer session token")] = None,
) -> str:
    """Validate bearer session token or issue a guest session identifier.

    Args:
        authorization: HTTP Authorization header.

    Returns:
        str: Validated session UUID.

    Raises:
        HTTPException: If token is provided but invalid/expired.
    """
    if not authorization:
        # Default anonymous guest session for zero-friction evaluation
        return "guest-evaluator-session"

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'.",
        )

    try:
        session_id = verify_session_token(parts[1])
        return session_id
    except SecurityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired session token: {exc}",
        ) from exc


def get_db_session() -> Generator[Session, None, None]:
    """Dependency yielding a transactional SQLAlchemy session.

    Yields:
        Session: Database session.
    """
    yield from get_db()


def get_llm() -> LLMProvider:
    """Dependency providing the active LLM engine.

    Returns:
        LLMProvider: LLM provider instance.
    """
    return get_llm_provider()
