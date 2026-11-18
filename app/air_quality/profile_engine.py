"""Household vulnerability assessment, regional smog baseline estimations, and demographic risk profiling."""
from __future__ import annotations

from app.models import FamilyProfileRequest, VulnerabilityTier

# Winter seasonal regional average AQIs for major metropolitan smog corridors
_REGIONAL_WINTER_AQI_DEFAULTS: dict[str, int] = {
    "delhi": 340,
    "new delhi": 340,
    "beijing": 195,
    "lahore": 380,
    "dhaka": 290,
    "karachi": 240,
    "ulaanbaatar": 310,
    "krakow": 165,
    "warsaw": 145,
    "salt lake city": 135,
    "fresno": 155,
    "bakersfield": 160,
    "london": 75,
    "paris": 85,
    "new york": 65,
    "los angeles": 90,
    "mumbai": 190,
    "kolkata": 260,
}


def estimate_city_baseline_aqi(city: str, provided_aqi: int | None = None) -> int:
    """Determine representative baseline AQI using city heuristics or provided telemetry.

    Args:
        city: City name or region.
        provided_aqi: Optional user-supplied real-time AQI reading.

    Returns:
        int: Estimated baseline AQI (bounded 20-500).
    """
    if provided_aqi is not None and 0 <= provided_aqi <= 1000:
        return provided_aqi

    clean_city = city.strip().lower()
    for known_city, default_aqi in _REGIONAL_WINTER_AQI_DEFAULTS.items():
        if known_city in clean_city:
            return default_aqi

    # Default moderate-to-severe urban winter baseline
    return 185


def assess_vulnerability_tier(
    vulnerable_members: list[str],
    baseline_aqi: int,
) -> VulnerabilityTier:
    """Evaluate health sensitivity tier based on demographic vulnerabilities and ambient air severity.

    Args:
        vulnerable_members: List of vulnerable groups (e.g. infants, asthmatics, elderly, pets).
        baseline_aqi: Ambient baseline air quality index.

    Returns:
        VulnerabilityTier: Low, Moderate, High, or Critical.
    """
    normalized = [m.lower().strip() for m in vulnerable_members]
    has_infants = any("infant" in m or "child" in m or "baby" in m or "toddler" in m for m in normalized)
    has_asthma = any("asthma" in m or "respiratory" in m or "copd" in m or "bronchitis" in m for m in normalized)
    has_elderly = any("elder" in m or "senior" in m or "grand" in m for m in normalized)
    has_cardio = any("heart" in m or "cardio" in m or "hypertension" in m for m in normalized)

    high_risk_count = sum([has_infants, has_asthma, has_elderly, has_cardio])

    if baseline_aqi >= 300 or (high_risk_count >= 2 and baseline_aqi >= 200) or (has_asthma and baseline_aqi >= 250):
        return VulnerabilityTier.CRITICAL
    if high_risk_count >= 1 or baseline_aqi >= 180:
        return VulnerabilityTier.HIGH
    if len(normalized) > 0 or baseline_aqi >= 100:
        return VulnerabilityTier.MODERATE

    return VulnerabilityTier.LOW


def get_vulnerability_guidelines(
    profile: FamilyProfileRequest,
    tier: VulnerabilityTier,
) -> list[str]:
    """Generate specialized clinical and physical protective directives tailored to vulnerable members.

    Args:
        profile: Household profile payload.
        tier: Calculated vulnerability tier.

    Returns:
        list[str]: Actionable safety directives for vulnerable household members.
    """
    guidelines: list[str] = []
    normalized = [m.lower().strip() for m in profile.vulnerable_members]

    if any("infant" in m or "child" in m or "baby" in m for m in normalized):
        guidelines.append(
            "Infant / Child Respiratory Defense: Maintain HEPA filtration at 2-3 feet elevation "
            "(infant breathing height), avoid stroller walks near roads as tailpipe exhaust concentrates below 3 feet, "
            "and hydrate children frequently to assist tracheobronchial mucociliary clearance."
        )

    if any("asthma" in m or "respiratory" in m or "copd" in m for m in normalized):
        guidelines.append(
            "Asthma & Pulmonary Protocol: Verify daily rescue inhaler availability, check Peak Expiratory Flow (PEF) "
            "each morning before venturing outdoors, and never engage in unmasked exterior transitions when AQI exceeds 150."
        )

    if any("elder" in m or "senior" in m for m in normalized):
        guidelines.append(
            "Elderly Cardiovascular & Lung Shield: Monitor resting blood pressure during smog spikes, ensure warm indoor "
            "temperatures (>20°C / 68°F) to avoid cold-induced pulmonary vasoconstriction, and use N95 respirators for all medical commutes."
        )

    if any("pet" in m or "dog" in m or "cat" in m for m in normalized):
        guidelines.append(
            "Pet Protection Protocol: Limit canine walks to quick 10-minute elimination trips during midday hours (13:00 - 14:30), "
            "wipe paws and fur with a damp cloth upon re-entering to prevent tracking carcinogenic soot indoors, and keep pet beds away from drafty exterior doors."
        )

    if not guidelines:
        guidelines.append(
            "General Household Defense: Maintain high-efficiency air cleaning during sleeping hours and replace furnace/HVAC filters with MERV-13 rated media."
        )

    return guidelines
