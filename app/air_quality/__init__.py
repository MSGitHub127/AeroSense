"""Air quality calculation engines, diurnal routine generators, and IAQ intervention models."""
from __future__ import annotations

from app.air_quality.alternatives_engine import generate_sustainable_alternatives
from app.air_quality.dossier_compiler import compile_family_air_dossier
from app.air_quality.iaq_hacks import get_curated_iaq_hacks
from app.air_quality.impact_calculator import calculate_personal_impact
from app.air_quality.profile_engine import (
    assess_vulnerability_tier,
    estimate_city_baseline_aqi,
    get_vulnerability_guidelines,
)
from app.air_quality.routine_engine import (
    calculate_diurnal_smog_curve,
    generate_daily_routines,
)

__all__ = [
    "assess_vulnerability_tier",
    "calculate_diurnal_smog_curve",
    "calculate_personal_impact",
    "compile_family_air_dossier",
    "estimate_city_baseline_aqi",
    "generate_daily_routines",
    "generate_sustainable_alternatives",
    "get_curated_iaq_hacks",
    "get_vulnerability_guidelines",
]
