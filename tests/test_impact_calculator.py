"""Unit tests for personal health dosimetry and cigarette smoke equivalence calculations."""
from __future__ import annotations

from app.air_quality.impact_calculator import calculate_personal_impact


def test_calculate_personal_impact_standard_scenario():
    """Verify calculated avoided lung dose and Berkeley Earth cigarette equivalence."""
    impact = calculate_personal_impact(
        baseline_aqi=300,
        exposure_reduction_pct=50.0,
        annual_co2_kg_saved=1500.0,
        num_household_members=3,
    )
    # At AQI 300, PM2.5 = 216 ug/m3. Gross intake = 3240 ug/day. 50% avoided = ~1620 ug/day.
    assert impact.daily_pm25_lung_dose_avoided_ug > 1000.0
    assert impact.annual_pm25_lung_dose_avoided_mg > 1000.0
    assert impact.equivalent_cigarettes_avoided > 1000.0
    assert impact.respiratory_risk_reduction_pct >= 50.0
    assert impact.annual_co2_saved_kg == 1500.0


def test_impact_bounds_and_clamping():
    """Ensure exposure reduction fraction and risk reduction stay within biological limits."""
    impact_low = calculate_personal_impact(
        baseline_aqi=50,
        exposure_reduction_pct=5.0,  # Clamped to min 10%
        annual_co2_kg_saved=0.0,
        num_household_members=1,
    )
    assert impact_low.respiratory_risk_reduction_pct >= 12.0

    impact_high = calculate_personal_impact(
        baseline_aqi=800,
        exposure_reduction_pct=99.0,  # Clamped to max 90%
        annual_co2_kg_saved=5000.0,
        num_household_members=5,
    )
    assert impact_high.respiratory_risk_reduction_pct <= 78.0
