"""Advisory domain service coordinating profile ingestion, intelligence generation, and secure persistence."""
from __future__ import annotations

import json
import uuid

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
from app.exceptions import ProfileNotFoundError, SecurityValidationError
from app.models import (
    AlternativesResponse,
    AvertedActionRecord,
    DailyRoutinesResponse,
    FamilyProfileRecord,
    FamilyProfileRequest,
    FullAirQualityAdvisoryResponse,
    IAQHacksResponse,
    ImpactMetrics,
    ProfileSummaryResponse,
    VulnerabilityTier,
)
from app.security import decrypt_pii, detect_prompt_injection, encrypt_pii, redact_pii


class AdvisoryService:
    """Enterprise service coordinating air quality intelligence, encryption, and transactional persistence."""

    @classmethod
    def _validate_and_sanitize_intake(
        cls,
        payload: FamilyProfileRequest,
    ) -> tuple[str, str, list[str]]:
        """Validate against prompt injection and redact inadvertent PII."""
        combined_text = f"{payload.household_name} {payload.location_city} {' '.join(payload.vulnerable_members)}"
        if detect_prompt_injection(combined_text):
            raise SecurityValidationError("Security violation: Inbound profile contains forbidden prompt injection patterns.")

        clean_household = redact_pii(payload.household_name)
        clean_city = redact_pii(payload.location_city)
        clean_members = [redact_pii(m) for m in payload.vulnerable_members]
        return clean_household, clean_city, clean_members

    @classmethod
    def _synthesize_intelligence(
        cls,
        payload: FamilyProfileRequest,
        clean_city: str,
        clean_members: list[str],
    ) -> tuple[int, VulnerabilityTier, DailyRoutinesResponse, IAQHacksResponse, AlternativesResponse, ImpactMetrics, str]:
        """Orchestrate domain intelligence calculations across all four atmospheric engines."""
        baseline_aqi = estimate_city_baseline_aqi(clean_city, payload.baseline_aqi)
        vuln_tier = assess_vulnerability_tier(clean_members, baseline_aqi)
        vuln_guidelines = get_vulnerability_guidelines(payload, vuln_tier)

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

        return baseline_aqi, vuln_tier, routines, iaq_hacks, alternatives, impact, action_plan_md

    @classmethod
    def _persist_encrypted_profile(
        cls,
        profile_id: str,
        session_id: str,
        payload: FamilyProfileRequest,
        clean_household: str,
        clean_city: str,
        clean_members: list[str],
        baseline_aqi: int,
        vuln_tier: VulnerabilityTier,
        routines: DailyRoutinesResponse,
        iaq_hacks: IAQHacksResponse,
        alternatives: AlternativesResponse,
        impact: ImpactMetrics,
        action_plan_md: str,
        db: Session,
    ) -> None:
        """Encrypt sensitive plan details and persist relational database records."""
        profile_data = {
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
        encrypted_blob = encrypt_pii(json.dumps(profile_data))

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

        for alt in alternatives.alternatives:
            action_rec = AvertedActionRecord(
                profile_id=profile_id,
                action_type=alt.habit_category,
                pm25_avoided_ug=alt.local_pm25_averted_grams * 1_000_000,
                co2_saved_kg=alt.annual_co2_kg_saved,
            )
            db.add(action_rec)

        db.commit()

    @classmethod
    def create_advisory_plan(
        cls,
        payload: FamilyProfileRequest,
        session_id: str,
        db: Session,
    ) -> FullAirQualityAdvisoryResponse:
        """Process household intake, synthesize multi-engine recommendations, and securely persist.

        Args:
            payload: Validated family profile request.
            session_id: Active session UUID.
            db: Transactional database session.

        Returns:
            FullAirQualityAdvisoryResponse: Complete synthesized air action dossier.
        """
        clean_household, clean_city, clean_members = cls._validate_and_sanitize_intake(payload)
        (
            baseline_aqi,
            vuln_tier,
            routines,
            iaq_hacks,
            alternatives,
            impact,
            action_plan_md,
        ) = cls._synthesize_intelligence(payload, clean_city, clean_members)

        profile_id = str(uuid.uuid4())
        cls._persist_encrypted_profile(
            profile_id=profile_id,
            session_id=session_id,
            payload=payload,
            clean_household=clean_household,
            clean_city=clean_city,
            clean_members=clean_members,
            baseline_aqi=baseline_aqi,
            vuln_tier=vuln_tier,
            routines=routines,
            iaq_hacks=iaq_hacks,
            alternatives=alternatives,
            impact=impact,
            action_plan_md=action_plan_md,
            db=db,
        )

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

    @staticmethod
    def get_advisory_by_id(profile_id: str, db: Session) -> FullAirQualityAdvisoryResponse:
        """Fetch stored family advisory and decrypt cached plan details.

        Args:
            profile_id: Advisory profile UUID.
            db: Database session.

        Returns:
            FullAirQualityAdvisoryResponse: Reconstructed advisory.

        Raises:
            ProfileNotFoundError: If profile ID is not found.
        """
        record = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.id == profile_id).first()
        if not record:
            raise ProfileNotFoundError(f"Profile '{profile_id}' not found.")

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

    @staticmethod
    def list_advisories_for_session(session_id: str, db: Session) -> list[ProfileSummaryResponse]:
        """Retrieve metadata of all advisories linked to current session.

        Args:
            session_id: Session UUID.
            db: Database session.

        Returns:
            list[ProfileSummaryResponse]: Typed list of profile metadata summaries.
        """
        records = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.session_id == session_id).all()
        return [
            ProfileSummaryResponse(
                id=r.id,
                household_name=r.household_name,
                location_city=r.location_city,
                estimated_baseline_aqi=r.estimated_baseline_aqi,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
            for r in records
        ]
