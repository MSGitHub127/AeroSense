"""Router calculating diurnal winter smog curves and exposure-minimized daily routines."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.air_quality.routine_engine import generate_daily_routines
from app.models import CommuteMode, DailyRoutinesResponse

router = APIRouter(prefix="/api/routines", tags=["Daily Routines"])


class RoutineCalculationRequest(BaseModel):
    """Payload for calculating diurnal smog curve and routine timing adjustments."""

    baseline_aqi: int = Field(
        default=180,
        ge=0,
        le=1000,
        description="Current ambient AQI",
    )
    city: str = Field(
        default="Metropolitan Region",
        min_length=2,
        max_length=120,
        description="Target city or metropolitan area",
    )
    commute_mode: CommuteMode = Field(
        default=CommuteMode.CAR_SOLO,
        description="Current commuting mode",
    )


@router.post("/calculate", response_model=DailyRoutinesResponse, summary="Calculate diurnal smog curve and optimized routines")
def calculate_routines(payload: RoutineCalculationRequest) -> DailyRoutinesResponse:
    """Generate diurnal air quality intervals and personalized timing shifts for core routines.

    Args:
        payload: Calculation request parameters.

    Returns:
        DailyRoutinesResponse: Hourly diurnal curve and shift recommendations.
    """
    return generate_daily_routines(
        baseline_aqi=payload.baseline_aqi,
        city=payload.city,
        commute_mode=payload.commute_mode.value,
    )
