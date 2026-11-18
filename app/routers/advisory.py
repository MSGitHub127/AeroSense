"""Comprehensive advisory router synthesizing profile ingestion, encryption, and holistic plan formulation."""
from __future__ import annotations

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.air_quality.alternatives_engine import generate_sustainable_alternatives
from app.air_quality.dossier_compiler import compile_family_air_dossier
from app.air_quality.iaq_hacks import get_curated_iaq_hacks
from app.air_quality.impact_calculator import calculate_personal_impact
from app.air_quality.profile_engine import (
    assess_vulnerability_tier,
    estimate_city_baseline_aqi,
    get_vulnerability_guidelines,
)
from app.air_quality.routine_engine import generate_daily_routines
from app.deps import get_current_session_id, get_db_session
from app.models import (
    AvertedActionRecord,
    FamilyProfileRecord,
    FamilyProfileRequest,
    FullAirQualityAdvisoryResponse,
    VulnerabilityTier,
)
from app.security import decrypt_pii, detect_prompt_injection, encrypt_pii, redact_pii

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

    Raises:
        HTTPException: If prompt injection is detected.
    """
    # Security: check for prompt injection in free-text fields
    combined_text = f"{payload.household_name} {payload.location_city} {' '.join(payload.vulnerable_members)}"
    if detect_prompt_injection(combined_text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security violation: Inbound profile contains forbidden prompt injection patterns.",
        )

    # Sanitize and redact any inadvertent PII
    clean_household = redact_pii(payload.household_name)
    clean_city = redact_pii(payload.location_city)
    clean_members = [redact_pii(m) for m in payload.vulnerable_members]

    # Calculate air quality parameters
    baseline_aqi = estimate_city_baseline_aqi(clean_city, payload.baseline_aqi)
    vuln_tier = assess_vulnerability_tier(clean_members, baseline_aqi)
    vuln_guidelines = get_vulnerability_guidelines(payload, vuln_tier)

    # Generate core domain modules
    routines = generate_daily_routines(baseline_aqi, clean_city, payload.commute_mode.value)
    iaq_hacks = get_curated_iaq_hacks(payload.home_type, payload.cooking_fuel, payload.has_hepa_purifier)
    alternatives = generate_sustainable_alternatives(
        payload.commute_mode, payload.cooking_fuel, payload.home_type, clean_city
    )

    household_count = max(len(clean_members) + 1, 2)
    impact = calculate_personal_impact(
        baseline_aqi=baseline_aqi,
        exposure_reduction_pct=routines.overall_daily_exposure_reduction_pct,
        annual_co2_kg_saved=alternatives.total_annual_co2_saved_kg,
        num_household_members=household_count,
    )

    action_plan_md = compile_family_air_dossier(
        profile=payload,
        estimated_aqi=baseline_aqi,
        vulnerability_tier=vuln_tier,
        routines=routines,
        iaq_hacks=iaq_hacks,
        alternatives=alternatives,
        impact=impact,
        vulnerability_guidelines=vuln_guidelines,
    )

    profile_id = str(uuid.uuid4())

    # Encrypt structured payload for zero-trust storage at rest
    profile_data_to_encrypt = {
        "vulnerable_members": clean_members,
        "cooking_fuel": payload.cooking_fuel.value,
        "commute_mode": payload.commute_mode.value,
        "has_hepa": payload.has_hepa_purifier,
        "vulnerability_tier": vuln_tier.value,
        "routines": routines.model_dump(),
        "iaq_hacks": iaq_hacks.model_dump(),
        "alternatives": alternatives.model_dump(),
        "impact": impact.model_dump(),
        "action_plan_markdown": action_plan_md,
    }
    encrypted_blob = encrypt_pii(json.dumps(profile_data_to_encrypt))

    # Persist in Database
    record = FamilyProfileRecord(
        id=profile_id,
        session_id=session_id,
        household_name=clean_household,
        location_city=clean_city,
        home_type=payload.home_type.value,
        estimated_baseline_aqi=baseline_aqi,
        encrypted_details=encrypted_blob,
    )
    db.add(record)

    # Persist individual averted actions for analytics
    for alt in alternatives.alternatives:
        action_rec = AvertedActionRecord(
            profile_id=profile_id,
            action_type=alt.habit_category,
            pm25_avoided_ug=alt.local_pm25_averted_grams * 1_000_000,
            co2_saved_kg=alt.annual_co2_kg_saved,
        )
        db.add(action_rec)

    db.commit()

    return FullAirQualityAdvisoryResponse(
        profile_id=profile_id,
        household_name=clean_household,
        location_city=clean_city,
        current_estimated_aqi=baseline_aqi,
        vulnerability_tier=vuln_tier,
        routines=routines,
        iaq_hacks=iaq_hacks,
        alternatives=alternatives,
        impact=impact,
        action_plan_markdown=action_plan_md,
    )


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

    Raises:
        HTTPException: If profile ID is not found.
    """
    record = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.id == profile_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '{profile_id}' not found.",
        )

    decrypted_str = decrypt_pii(record.encrypted_details)
    details = json.loads(decrypted_str)

    return FullAirQualityAdvisoryResponse(
        profile_id=record.id,
        household_name=record.household_name,
        location_city=record.location_city,
        current_estimated_aqi=record.estimated_baseline_aqi,
        vulnerability_tier=VulnerabilityTier(details.get("vulnerability_tier", "moderate")),
        routines=details["routines"],
        iaq_hacks=details["iaq_hacks"],
        alternatives=details["alternatives"],
        impact=details["impact"],
        action_plan_markdown=details["action_plan_markdown"],
    )


@router.get("", response_model=list[dict], summary="List stored profiles for the active session")
def list_session_profiles(
    session_id: Annotated[str, Depends(get_current_session_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[dict]:
    """Retrieve metadata of all advisories linked to current session.

    Args:
        session_id: Session UUID.
        db: Database session.

    Returns:
        list[dict]: List of profile metadata summaries.
    """
    records = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.session_id == session_id).all()
    return [
        {
            "id": r.id,
            "household_name": r.household_name,
            "location_city": r.location_city,
            "estimated_baseline_aqi": r.estimated_baseline_aqi,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
