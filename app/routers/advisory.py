"""Advisory router delegating intake, plan formulation, and retrieval to the service layer."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_session_id, get_db_session
from app.models import (
    FamilyProfileRequest,
    FullAirQualityAdvisoryResponse,
    ProfileSummaryResponse,
)
from app.services.advisory_service import AdvisoryService

router = APIRouter(prefix="/api/advisory", tags=["Air Advisory"])


@router.post("", response_model=FullAirQualityAdvisoryResponse, summary="Create family profile and synthesize air advisory")
def create_advisory(
    payload: FamilyProfileRequest,
    session_id: Annotated[str, Depends(get_current_session_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> FullAirQualityAdvisoryResponse:
    """Ingest household profile, evaluate vulnerabilities, optimize diurnal routines, and calculate avoided exposures.

    Args:
        payload: Household characteristics and vulnerabilities.
        session_id: Validated session UUID.
        db: Transactional database session.

    Returns:
        FullAirQualityAdvisoryResponse: Complete synthesized air action plan.
    """
    return AdvisoryService.create_advisory_plan(payload, session_id, db)


@router.get("/{profile_id}", response_model=FullAirQualityAdvisoryResponse, summary="Retrieve previously generated air advisory")
def get_advisory(
    profile_id: str,
    db: Annotated[Session, Depends(get_db_session)],
) -> FullAirQualityAdvisoryResponse:
    """Fetch stored family advisory and decrypt cached plan details.

    Args:
        profile_id: Advisory profile UUID.
        db: Database session.

    Returns:
        FullAirQualityAdvisoryResponse: Reconstructed advisory.
    """
    return AdvisoryService.get_advisory_by_id(profile_id, db)


@router.get("", response_model=list[ProfileSummaryResponse], summary="List stored profiles for the active session")
def list_session_profiles(
    session_id: Annotated[str, Depends(get_current_session_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ProfileSummaryResponse]:
    """Retrieve typed metadata of all advisories linked to current session.

    Args:
        session_id: Session UUID.
        db: Database session.

    Returns:
        list[ProfileSummaryResponse]: Strongly typed list of profile metadata summaries.
    """
    return AdvisoryService.list_advisories_for_session(session_id, db)
