"""Diurnal winter smog curve modeling, low-emission daily routines, and exposure mitigation."""
from __future__ import annotations

from app.models import DailyRoutinesResponse, DiurnalAQIWindow, RoutineRecommendation


def calculate_diurnal_smog_curve(baseline_aqi: int) -> list[DiurnalAQIWindow]:
    """Calculate hourly diurnal particulate patterns driven by winter atmospheric thermal inversions.

    Args:
        baseline_aqi: Baseline 24-hour mean AQI.

    Returns:
        list[DiurnalAQIWindow]: 5 chronological windows with predicted PM2.5 and activity advisories.
    """
    # Multipliers representing winter inversion boundary layer dynamics
    # Early morning & night trap ground emissions; mid-afternoon solar heating raises ceiling
    windows_config = [
        {
            "time_range": "05:00 - 09:30",
            "multiplier": 1.45,
            "category": "Hazardous / Severe Inversion",
            "recommended": ["Indoor morning prep with air filtration running", "Remote work / delayed departure if possible"],
            "avoid": ["Morning jogging or outdoor cardio", "Opening windows or exterior ventilation"],
        },
        {
            "time_range": "09:30 - 12:30",
            "multiplier": 1.05,
            "category": "Unhealthy",
            "recommended": ["Essential errands with certified N95/KF94 masks", "Vehicle cabin set to air recirculation mode"],
            "avoid": ["Prolonged outdoor construction or manual exertion"],
        },
        {
            "time_range": "12:30 - 15:30",
            "multiplier": 0.65,
            "category": "Moderate / Optimal Air Window",
            "recommended": [
                "15-minute cross-ventilation home air flush",
                "Outdoor dog walking and light physical activities",
                "School playground recess permitted",
            ],
            "avoid": ["Idling combustion engines in residential driveways"],
        },
        {
            "time_range": "15:30 - 18:30",
            "multiplier": 1.10,
            "category": "Unhealthy for Sensitive Groups",
            "recommended": ["Afternoon school pickup with masks ready", "Close all windows before evening inversion sets in"],
            "avoid": ["Rush hour walking along major arterial traffic routes"],
        },
        {
            "time_range": "18:30 - 05:00",
            "multiplier": 1.40,
            "category": "Very Unhealthy / Evening Accumulation",
            "recommended": [
                "Continuous bedroom HEPA filtration",
                "Sealing door drafts and exterior wall vents",
                "Indoor social and family activities",
            ],
            "avoid": ["Outdoor night workouts", "Using wood-burning stoves or fireplaces"],
        },
    ]

    result: list[DiurnalAQIWindow] = []
    # Conversion approximation: 1 AQI point ~ 0.7 µg/m³ PM2.5 in typical winter smoke regimes
    for w in windows_config:
        pm25 = round((baseline_aqi * 0.72) * w["multiplier"], 1)
        result.append(
            DiurnalAQIWindow(
                time_range=w["time_range"],
                predicted_pm25=pm25,
                aqi_category=w["category"],
                recommended_activities=w["recommended"],
                activities_to_avoid=w["avoid"],
            )
        )
    return result


def generate_daily_routines(baseline_aqi: int, city: str, commute_mode: str) -> DailyRoutinesResponse:
    """Formulate targeted timing shifts for core daily family routines to slash inhaled particulate dosage.

    Args:
        baseline_aqi: Representative baseline AQI.
        city: Target metropolitan area.
        commute_mode: Current primary transit mode.

    Returns:
        DailyRoutinesResponse: Optimized timings, rationale, and percentage exposure saved.
    """
    diurnal = calculate_diurnal_smog_curve(baseline_aqi)

    # 1. Commute Routine
    if commute_mode in ("walking", "cycling"):
        commute = RoutineRecommendation(
            activity_name="Work / Office Commute",
            standard_time="08:15 AM - 09:00 AM",
            optimized_time="07:15 AM OR Post-09:45 AM",
            reasoning=(
                f"In {city}, peak vehicular exhaust synchronizes with the cold surface inversion between 08:00 and 09:15 AM. "
                "Commuting before 07:30 AM or shifting departure past 09:45 AM bypasses the steepest particulate spike."
            ),
            pm25_exposure_saved_pct=42.0,
        )
    else:
        commute = RoutineRecommendation(
            activity_name="Vehicle / Transit Commute",
            standard_time="08:00 AM - 08:45 AM",
            optimized_time="07:30 AM (Cabin Air Recirculation Active)",
            reasoning=(
                "Enabling internal cabin air recirculation with a fresh cabin MERV-13 filter prevents vehicular tunnel fumes "
                "from penetrating the vehicle interior, cutting in-cabin PM2.5 by up to 55%."
            ),
            pm25_exposure_saved_pct=48.5,
        )

    # 2. School Dropoff & Pickup
    school = RoutineRecommendation(
        activity_name="School Dropoff & Children Morning Arrival",
        standard_time="08:00 AM Dropoff / 03:00 PM Pickup",
        optimized_time="Equip N95/KF94 Mask for Dropoff / Stagger Pickup past 03:30 PM",
        reasoning=(
            "Idling queues of diesel buses and parent cars create concentrated ground micro-plumes at school perimeters. "
            "Equipping children with well-fitted KF94/N95 masks and parking 100 meters away prevents acute exposure."
        ),
        pm25_exposure_saved_pct=52.0,
    )

    # 3. Exercise & Fitness
    exercise = RoutineRecommendation(
        activity_name="Outdoor Exercise & Cardiovascular Fitness",
        standard_time="06:30 AM Morning Run",
        optimized_time="13:30 PM - 14:30 PM (Or Filtered Indoor Gym)",
        reasoning=(
            "Morning cardiovascular exercise during winter smog forces up to 8x higher air volume deep into alveolar lung tissues "
            "during the day's highest pollution peak. Shift workouts to the solar dispersion window (13:30 PM) or indoors."
        ),
        pm25_exposure_saved_pct=68.0,
    )

    # 4. Natural Home Ventilation Flush
    ventilation = RoutineRecommendation(
        activity_name="Home Air Flush & CO2 Dissipation",
        standard_time="Continuous cracked windows or random opening",
        optimized_time="13:00 PM - 13:20 PM (Strict 20-Minute Cross-Flush)",
        reasoning=(
            "Opening windows when outdoor PM2.5 is at its diurnal minimum (13:00 - 13:20 PM) purges indoor stale carbon dioxide "
            "with the lowest possible particulate penalty. Seal windows immediately after and run HEPA on high for 30 minutes."
        ),
        pm25_exposure_saved_pct=45.0,
    )

    avg_saved = round((commute.pm25_exposure_saved_pct + school.pm25_exposure_saved_pct + exercise.pm25_exposure_saved_pct + ventilation.pm25_exposure_saved_pct) / 4.0, 1)

    return DailyRoutinesResponse(
        diurnal_windows=diurnal,
        commute_routine=commute,
        school_routine=school,
        exercise_routine=exercise,
        ventilation_routine=ventilation,
        overall_daily_exposure_reduction_pct=avg_saved,
    )
