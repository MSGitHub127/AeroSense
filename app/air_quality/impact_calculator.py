"""Personalized health impact, lung particulate dosage mitigation, and cigarette smoke equivalence calculator."""
from __future__ import annotations

from app.models import ImpactMetrics


def calculate_personal_impact(
    baseline_aqi: int,
    exposure_reduction_pct: float,
    annual_co2_kg_saved: float,
    num_household_members: int = 3,
) -> ImpactMetrics:
    """Calculate direct personal and environmental health impact metrics.

    Calculations are grounded in environmental health dosimetry and Berkeley Earth PM2.5 equivalence formulas.
    Average human inhalation volume: 15 m³/day.
    1 Cigarette equivalence: ~22 µg/m³ PM2.5 24-hour exposure (~330 µg inhaled PM2.5 mass).

    Args:
        baseline_aqi: Local ambient baseline AQI.
        exposure_reduction_pct: Percentage reduction achieved through daily routine shifts and IAQ hacks.
        annual_co2_kg_saved: Direct CO2 emissions avoided from clean alternatives.
        num_household_members: Count of family members protected.

    Returns:
        ImpactMetrics: Quantified daily/annual particulate lung dose avoided, cigarette equivalence, and risk reduction.
    """
    # 1. Ambient PM2.5 concentration (µg/m³) from AQI
    ambient_pm25_ug_m3 = baseline_aqi * 0.72

    # 2. Daily baseline lung intake without protective intervention (15 m³ daily minute ventilation)
    daily_volume_m3 = 15.0
    daily_unmitigated_dose_ug = ambient_pm25_ug_m3 * daily_volume_m3

    # 3. Daily lung dose avoided per person
    fraction_saved = min(max(exposure_reduction_pct / 100.0, 0.10), 0.90)
    daily_dose_avoided_ug = round(daily_unmitigated_dose_ug * fraction_saved, 1)

    # 4. Annual avoided dose in milligrams (mg) across the household
    annual_dose_avoided_mg = round((daily_dose_avoided_ug * 365.0 * num_household_members) / 1000.0, 1)

    # 5. Cigarette equivalence avoided (Berkeley Earth standard: 330 µg inhaled = 1 cigarette)
    # Calculated on an annual family basis
    daily_cigs_per_person = daily_dose_avoided_ug / 330.0
    annual_family_cigarettes_avoided = round(daily_cigs_per_person * 365.0 * num_household_members, 1)

    # 6. Respiratory risk reduction percentage (grounded in WHO acute symptom curve)
    # Approx 6% acute symptom reduction per 10 µg/m³ exposure averted, capped at 78%
    pm25_concentration_reduction = ambient_pm25_ug_m3 * fraction_saved
    risk_reduction_pct = round(min(78.0, max(12.0, (pm25_concentration_reduction / 10.0) * 6.2)), 1)

    return ImpactMetrics(
        daily_pm25_lung_dose_avoided_ug=daily_dose_avoided_ug,
        annual_pm25_lung_dose_avoided_mg=annual_dose_avoided_mg,
        equivalent_cigarettes_avoided=annual_family_cigarettes_avoided,
        annual_co2_saved_kg=round(annual_co2_kg_saved, 1),
        respiratory_risk_reduction_pct=risk_reduction_pct,
    )
