"""Session management router issuing privacy-preserving anonymous JWT tokens."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.security import create_anonymous_session_token

router = APIRouter(prefix="/api/session", tags=["Session"])


class SessionResponse(BaseModel):
    """Anonymous session token response."""

    session_token: str = Field(..., description="Signed anonymous JWT bearer token")
    token_type: str = Field(default="Bearer", description="HTTP authorization scheme")
    expires_in_hours: int = Field(default=24, description="Token validity window in hours")


@router.post("", response_model=SessionResponse, summary="Create an anonymous privacy-preserving session")
def create_session() -> SessionResponse:
    """Issue a new cryptographic bearer token allowing stateless user interactions without PII.

    Returns:
        SessionResponse: Signed JWT token.
    """
    token = create_anonymous_session_token()
    return SessionResponse(
        session_token=token,
        token_type="Bearer",
        expires_in_hours=24,
    )
