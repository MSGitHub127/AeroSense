"""Unit tests for demographic vulnerability assessment and city AQI estimation."""
from __future__ import annotations

from app.air_quality.profile_engine import (
    assess_vulnerability_tier,
    estimate_city_baseline_aqi,
    get_vulnerability_guidelines,
)
from app.models import CommuteMode, CookingFuel, FamilyProfileRequest, HomeType, VulnerabilityTier


def test_estimate_city_baseline_aqi_known_cities():
    """Verify regional winter baseline estimates for major smog basins."""
    assert estimate_city_baseline_aqi("Delhi") == 340
    assert estimate_city_baseline_aqi("New Delhi") == 340
    assert estimate_city_baseline_aqi("Beijing") == 195
    assert estimate_city_baseline_aqi("Lahore") == 380
    assert estimate_city_baseline_aqi("Salt Lake City") == 135
    assert estimate_city_baseline_aqi("London") == 75


def test_estimate_city_baseline_aqi_custom_telemetry():
    """Verify user-provided AQI takes precedence when valid."""
    assert estimate_city_baseline_aqi("Delhi", provided_aqi=450) == 450
    assert estimate_city_baseline_aqi("UnknownTown", provided_aqi=None) == 185


def test_assess_vulnerability_tier_critical():
    """Verify critical tier for high AQI combined with infants or asthmatics."""
    tier1 = assess_vulnerability_tier(["infant", "asthma"], baseline_aqi=260)
    assert tier1 == VulnerabilityTier.CRITICAL

    tier2 = assess_vulnerability_tier([], baseline_aqi=320)
    assert tier2 == VulnerabilityTier.CRITICAL


def test_assess_vulnerability_tier_high_and_moderate():
    """Verify high and moderate severity classifications."""
    tier_high = assess_vulnerability_tier(["elderly_grandparent"], baseline_aqi=150)
    assert tier_high == VulnerabilityTier.HIGH

    tier_mod = assess_vulnerability_tier(["dog_pet"], baseline_aqi=80)
    assert tier_mod == VulnerabilityTier.MODERATE

    tier_low = assess_vulnerability_tier([], baseline_aqi=45)
    assert tier_low == VulnerabilityTier.LOW


def test_get_vulnerability_guidelines_content():
    """Verify clinical and physical defense guidelines for sensitive groups."""
    payload = FamilyProfileRequest(
        household_name="Gupta",
        location_city="Delhi",
        home_type=HomeType.APARTMENT,
        cooking_fuel=CookingFuel.GAS,
        commute_mode=CommuteMode.CAR_SOLO,
        has_hepa_purifier=False,
        vulnerable_members=["infant_baby", "asthmatic_mother", "elderly_father", "dog"],
    )
    guidelines = get_vulnerability_guidelines(payload, VulnerabilityTier.CRITICAL)
    assert len(guidelines) >= 4

    joined = " ".join(guidelines).lower()
    assert "infant" in joined or "child" in joined
    assert "asthma" in joined or "inhaler" in joined
    assert "elderly" in joined or "blood pressure" in joined
    assert "pet" in joined or "paw" in joined
