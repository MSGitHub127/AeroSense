"""Router computing sustainable lifestyle alternatives and quantified emission offsets."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.air_quality.alternatives_engine import generate_sustainable_alternatives
from app.models import AlternativesResponse, CommuteMode, CookingFuel, HomeType

router = APIRouter(prefix="/api/alternatives", tags=["Sustainable Alternatives"])


class AlternativesCalculationRequest(BaseModel):
    """Payload for calculating personalized sustainable lifestyle substitutions."""

    commute_mode: CommuteMode = Field(
        default=CommuteMode.CAR_SOLO,
        description="Current commute mode",
    )
    cooking_fuel: CookingFuel = Field(
        default=CookingFuel.GAS,
        description="Current cooking fuel",
    )
    home_type: HomeType = Field(
        default=HomeType.APARTMENT,
        description="Dwelling structural type",
    )
    city: str = Field(
        default="Metropolitan Region",
        min_length=2,
        max_length=120,
        description="Target city name",
    )


@router.post("/calculate", response_model=AlternativesResponse, summary="Calculate sustainable alternatives and emissions avoided")
def calculate_alternatives(payload: AlternativesCalculationRequest) -> AlternativesResponse:
    """Generate high-impact sustainable lifestyle alternatives with annual avoided CO2 and PM2.5 metrics.

    Args:
        payload: Household alternatives request.

    Returns:
        AlternativesResponse: Calculated substitutions and cumulative emission offsets.
    """
    return generate_sustainable_alternatives(
        commute_mode=payload.commute_mode,
        cooking_fuel=payload.cooking_fuel,
        home_type=payload.home_type,
        city=payload.city,
    )
