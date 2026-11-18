"""Unit tests for diurnal winter smog curve calculation and routine optimization."""
from __future__ import annotations

from app.air_quality.routine_engine import (
    calculate_diurnal_smog_curve,
    generate_daily_routines,
)


def test_calculate_diurnal_smog_curve():
    """Verify 5 chronological windows and diurnal multiplier behavior."""
    windows = calculate_diurnal_smog_curve(baseline_aqi=200)
    assert len(windows) == 5

    # Early morning window (05:00 - 09:30) must have highest concentration
    morning = windows[0]
    assert "05:00" in morning.time_range
    assert morning.predicted_pm25 > 200

    # Midday window (12:30 - 15:30) must have nadir / optimal air
    midday = windows[2]
    assert "12:30" in midday.time_range
    assert midday.predicted_pm25 < morning.predicted_pm25
    assert "Moderate" in midday.aqi_category or "Optimal" in midday.aqi_category


def test_generate_daily_routines_car_commute():
    """Verify routine recommendations for vehicle commute mode."""
    routines = generate_daily_routines(
        baseline_aqi=300,
        city="Delhi",
        commute_mode="car_solo",
    )
    assert routines.commute_routine.pm25_exposure_saved_pct > 40.0
    assert "Recirculation" in routines.commute_routine.optimized_time
    assert routines.school_routine.pm25_exposure_saved_pct >= 50.0
    assert routines.exercise_routine.pm25_exposure_saved_pct >= 60.0
    assert routines.overall_daily_exposure_reduction_pct > 45.0


def test_generate_daily_routines_walking_commute():
    """Verify routine adjustments when family walks or cycles."""
    routines = generate_daily_routines(
        baseline_aqi=220,
        city="Lahore",
        commute_mode="walking",
    )
    assert "07:15 AM" in routines.commute_routine.optimized_time or "09:45" in routines.commute_routine.optimized_time
    assert routines.commute_routine.pm25_exposure_saved_pct >= 40.0
