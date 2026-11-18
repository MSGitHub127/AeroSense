"""Router providing curated Indoor Air Quality (IAQ) hacks and room prioritization."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.air_quality.iaq_hacks import get_curated_iaq_hacks
from app.models import CookingFuel, HomeType, IAQHacksResponse

router = APIRouter(prefix="/api/iaq", tags=["Indoor Air Quality"])


@router.get("/hacks", response_model=IAQHacksResponse, summary="Retrieve high-impact indoor air quality hacks")
def list_iaq_hacks(
    home_type: Annotated[HomeType, Query(description="Housing architecture")] = HomeType.APARTMENT,
    cooking_fuel: Annotated[CookingFuel, Query(description="Cooking stove fuel")] = CookingFuel.GAS,
    has_hepa: Annotated[bool, Query(description="Whether HEPA purifier is installed")] = False,
) -> IAQHacksResponse:
    """Provide tailored high-yield indoor air quality interventions and room priority order.

    Args:
        home_type: Dwelling type.
        cooking_fuel: Kitchen fuel type.
        has_hepa: HEPA availability.

    Returns:
        IAQHacksResponse: Prioritized interventions, costs, and instructions.
    """
    return get_curated_iaq_hacks(
        home_type=home_type,
        cooking_fuel=cooking_fuel,
        has_hepa=has_hepa,
    )
