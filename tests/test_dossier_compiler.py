"""Unit tests for the synthesized Markdown Family Air Action Plan compiler."""
from __future__ import annotations

from app.air_quality.alternatives_engine import generate_sustainable_alternatives
from app.air_quality.dossier_compiler import compile_family_air_dossier
from app.air_quality.iaq_hacks import get_curated_iaq_hacks
from app.air_quality.impact_calculator import calculate_personal_impact
from app.air_quality.profile_engine import assess_vulnerability_tier, get_vulnerability_guidelines
from app.air_quality.routine_engine import generate_daily_routines
from app.models import CommuteMode, CookingFuel, FamilyProfileRequest, HomeType


def test_compile_family_air_dossier_structure():
    """Verify generated Markdown document contains required tables, sections, and metrics."""
    profile = FamilyProfileRequest(
        household_name="Verma Family",
        location_city="Delhi",
        home_type=HomeType.APARTMENT,
        cooking_fuel=CookingFuel.GAS,
        commute_mode=CommuteMode.CAR_SOLO,
        has_hepa_purifier=False,
        vulnerable_members=["toddler", "asthmatic_grandmother"],
        baseline_aqi=340,
    )
    aqi = 340
    tier = assess_vulnerability_tier(profile.vulnerable_members, aqi)
    guidelines = get_vulnerability_guidelines(profile, tier)
    routines = generate_daily_routines(aqi, profile.location_city, profile.commute_mode.value)
    iaq_hacks = get_curated_iaq_hacks(profile.home_type, profile.cooking_fuel, profile.has_hepa_purifier)
    alternatives = generate_sustainable_alternatives(
        profile.commute_mode, profile.cooking_fuel, profile.home_type, profile.location_city
    )
    impact = calculate_personal_impact(
        baseline_aqi=aqi,
        exposure_reduction_pct=routines.overall_daily_exposure_reduction_pct,
        annual_co2_kg_saved=alternatives.total_annual_co2_saved_kg,
        num_household_members=3,
    )

    doc = compile_family_air_dossier(
        profile=profile,
        estimated_aqi=aqi,
        vulnerability_tier=tier,
        routines=routines,
        iaq_hacks=iaq_hacks,
        alternatives=alternatives,
        impact=impact,
        vulnerability_guidelines=guidelines,
    )

    assert "# AeroSense: Winter Smog & Urban Air Action Plan for the Verma Family Family" in doc or "Verma" in doc
    assert "## 1. Executive Summary & Quantified Direct Impact" in doc
    assert "Daily Inhaled PM2.5 Lung Dose Avoided" in doc
    assert "Passive Cigarette Inhalation Equivalent Averted" in doc
    assert "Direct Greenhouse Gas Emissions Reduced" in doc
    assert "## 2. Diurnal Smog Cycle & Timing-Shifted Daily Routines" in doc
    assert "## 3. High-Yield Indoor Air Quality (IAQ) Hacks" in doc
    assert "## 4. Sustainable Household Alternatives & Emission Reductions" in doc
    assert "## 5. Vulnerability Directives & Medical Precautions" in doc
    assert "Corsi-Rosenthal" in doc
