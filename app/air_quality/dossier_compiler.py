"""Synthesis compiler generating structured exportable Markdown Family Air Action Plans."""
from __future__ import annotations

from app.models import (
    AlternativesResponse,
    DailyRoutinesResponse,
    FamilyProfileRequest,
    IAQHacksResponse,
    ImpactMetrics,
    VulnerabilityTier,
)


def _build_header_and_summary(
    profile: FamilyProfileRequest,
    estimated_aqi: int,
    vulnerability_tier: VulnerabilityTier,
    impact: ImpactMetrics,
) -> list[str]:
    """Construct title, profile metadata headers, and quantified impact summary section."""
    dwelling = profile.home_type.value.replace("_", " ").title()
    stove = profile.cooking_fuel.value.title()
    transit = profile.commute_mode.value.title()
    return [
        f"# AeroSense: Winter Smog & Urban Air Action Plan for the {profile.household_name} Family",
        "",
        f"**Metropolitan Area:** {profile.location_city}  ",
        f"**Baseline Ambient Winter AQI:** {estimated_aqi}  ",
        f"**Household Health Vulnerability Tier:** {vulnerability_tier.value.upper()}  ",
        f"**Dwelling Type:** {dwelling} | **Stove Fuel:** {stove} | **Transit Mode:** {transit}",
        "",
        "---",
        "",
        "## 1. Executive Summary & Quantified Direct Impact",
        f"By implementing AeroSense's coordinated diurnal timing shifts, targeted indoor air quality hacks, and clean lifestyle substitutions, the **{profile.household_name}** household achieves:",
        "",
        f"- **Daily Inhaled PM2.5 Lung Dose Avoided:** `{impact.daily_pm25_lung_dose_avoided_ug:,} µg/day`",
        f"- **Annual Household Inhaled Particulates Prevented:** `{impact.annual_pm25_lung_dose_avoided_mg:,} mg/year`",
        f"- **Passive Cigarette Inhalation Equivalent Averted:** `{impact.equivalent_cigarettes_avoided:,} cigarettes/year` (Berkeley Earth Dosimetry)",
        f"- **Direct Greenhouse Gas Emissions Reduced:** `{impact.annual_co2_saved_kg:,} kg CO2/year`",
        f"- **Acute Respiratory Exacerbation Risk Reduced:** `{impact.respiratory_risk_reduction_pct}% reduction`",
        "",
        "---",
        "",
    ]


def _build_routines_section(routines: DailyRoutinesResponse) -> list[str]:
    """Construct diurnal atmospheric inversion windows table and timing-shifted daily routines."""
    lines = [
        "## 2. Diurnal Smog Cycle & Timing-Shifted Daily Routines",
        "Winter urban air pollution follows strict atmospheric thermal inversion dynamics: cold night air traps tailpipe and biomass smoke at surface level, while mid-afternoon solar heating briefly lifts the planetary boundary layer.",
        "",
        "### Diurnal Smog Windows & Activity Safety",
        "| Time Interval | Predicted PM2.5 | Air Quality Tier | Safe Household Activities | Activities to Avoid |",
        "|---|---|---|---|---|",
    ]

    for w in routines.diurnal_windows:
        rec_str = "; ".join(w.recommended_activities)
        avoid_str = "; ".join(w.activities_to_avoid)
        lines.append(f"| {w.time_range} | {w.predicted_pm25} µg/m³ | {w.aqi_category} | {rec_str} | {avoid_str} |")

    lines.extend([
        "",
        "### Optimized Daily Routines",
        f"- **Work / Commute:** Shift from `{routines.commute_routine.standard_time}` to `{routines.commute_routine.optimized_time}`.  ",
        f"  *Rationale:* {routines.commute_routine.reasoning}  ",
        f"  *Exposure Saved:* **{routines.commute_routine.pm25_exposure_saved_pct}%**",
        "",
        f"- **School Runs & Children Transit:** `{routines.school_routine.optimized_time}`.  ",
        f"  *Rationale:* {routines.school_routine.reasoning}  ",
        f"  *Exposure Saved:* **{routines.school_routine.pm25_exposure_saved_pct}%**",
        "",
        f"- **Physical Exercise & Cardio:** `{routines.exercise_routine.optimized_time}`.  ",
        f"  *Rationale:* {routines.exercise_routine.reasoning}  ",
        f"  *Exposure Saved:* **{routines.exercise_routine.pm25_exposure_saved_pct}%**",
        "",
        f"- **Home Air Flush & CO2 Dissipation:** `{routines.ventilation_routine.optimized_time}`.  ",
        f"  *Rationale:* {routines.ventilation_routine.reasoning}  ",
        f"  *Exposure Saved:* **{routines.ventilation_routine.pm25_exposure_saved_pct}%**",
        "",
        "---",
        "",
    ])
    return lines


def _build_iaq_section(iaq_hacks: IAQHacksResponse) -> list[str]:
    """Construct indoor air quality interventions, room priority rankings, and instructions."""
    lines = [
        "## 3. High-Yield Indoor Air Quality (IAQ) Hacks",
        "Indoor air during severe winter smog is often 2x to 5x more hazardous than outdoor air due to indoor entrapment of cooking fumes, NO2, and penetrating ultrafine aerosols.",
        "",
        "### Prioritized Room Defense Order",
    ]

    for i, room in enumerate(iaq_hacks.room_priority_order, 1):
        lines.append(f"{i}. {room}")

    lines.extend([
        "",
        "### Immediate Zero-Cost Action Tips",
    ])
    for tip in iaq_hacks.instant_action_tips:
        lines.append(f"- [x] {tip}")

    lines.extend([
        "",
        "### Step-by-Step Interventions",
    ])
    for hack in iaq_hacks.hacks:
        lines.append(f"#### {hack.hack_name} ({hack.category.title()} — Difficulty: {hack.difficulty})")
        lines.append(f"- **Estimated Cost:** ${hack.estimated_cost_usd:.2f} | **Indoor PM2.5 Reduction:** ~{hack.pm25_reduction_pct}%")
        lines.append("- **Equipment Required:** " + ", ".join(hack.equipment_needed))
        lines.append("- **Step-by-Step Instructions:**")
        for step in hack.step_by_step_instructions:
            lines.append(f"  1. {step}")
        lines.append("")

    lines.extend(["---", ""])
    return lines


def _build_alternatives_section(profile: FamilyProfileRequest, alternatives: AlternativesResponse) -> list[str]:
    """Construct sustainable lifestyle substitutions table and avoided emissions summary."""
    lines = [
        "## 4. Sustainable Household Alternatives & Emission Reductions",
        f"By adopting these community-conscious substitutions, the {profile.household_name} family directly abates local ground emissions that cause severe winter inversions.",
        "",
        "| Category | Current Habit | Clean Alternative | Annual CO2 Saved | Local PM2.5 Averted | Financial Impact |",
        "|---|---|---|---|---|---|",
    ]
    for alt in alternatives.alternatives:
        lines.append(
            f"| {alt.habit_category.title()} | {alt.current_habit} | {alt.recommended_alternative} | "
            f"{alt.annual_co2_kg_saved:,.0f} kg | {alt.local_pm25_averted_grams:,.0f} g | {alt.cost_implication} |"
        )

    lines.extend([
        "",
        f"**Combined Community Emission Abatement:** `{alternatives.total_annual_co2_saved_kg:,} kg CO2` and `{alternatives.total_local_pm25_averted_grams:,} grams PM2.5` kept out of local air sheds.",
        "",
        "---",
        "",
    ])
    return lines


def _build_vulnerability_section(vulnerability_guidelines: list[str]) -> list[str]:
    """Construct medical vulnerability directives and footer."""
    lines = [
        "## 5. Vulnerability Directives & Medical Precautions",
    ]
    for g in vulnerability_guidelines:
        lines.append(f"- {g}")

    lines.extend([
        "",
        "---",
        "",
        "*AeroSense Action Plan generated automatically with peer-reviewed atmospheric science dosimetry and Google Gemini intelligence.*",
    ])
    return lines


def compile_family_air_dossier(
    profile: FamilyProfileRequest,
    estimated_aqi: int,
    vulnerability_tier: VulnerabilityTier,
    routines: DailyRoutinesResponse,
    iaq_hacks: IAQHacksResponse,
    alternatives: AlternativesResponse,
    impact: ImpactMetrics,
    vulnerability_guidelines: list[str],
) -> str:
    """Compile a comprehensive, publication-grade Markdown Family Air Action Plan.

    Args:
        profile: Household profile request.
        estimated_aqi: Baseline ambient AQI.
        vulnerability_tier: Sensitivity classification.
        routines: Diurnal routine recommendations.
        iaq_hacks: Indoor air quality hacks.
        alternatives: Sustainable lifestyle alternatives.
        impact: Quantified personal health and emissions metrics.
        vulnerability_guidelines: Specialized protective guidelines.

    Returns:
        str: Fully formatted Markdown document.
    """
    sections = [
        *_build_header_and_summary(profile, estimated_aqi, vulnerability_tier, impact),
        *_build_routines_section(routines),
        *_build_iaq_section(iaq_hacks),
        *_build_alternatives_section(profile, alternatives),
        *_build_vulnerability_section(vulnerability_guidelines),
    ]
    return "\n".join(sections)
