"""Router formulating personalized lung particulate dosage avoided and cigarette equivalence metrics."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.air_quality.impact_calculator import calculate_personal_impact
from app.models import ImpactMetrics

router = APIRouter(prefix="/api/impact", tags=["Impact Dosimetry"])


class ImpactCalculationRequest(BaseModel):
    """Payload for calculating personalized health and environmental impact metrics."""

    baseline_aqi: int = Field(
        default=180,
        ge=0,
        le=1000,
        description="Ambient baseline AQI",
    )
    exposure_reduction_pct: float = Field(
        default=55.0,
        ge=0.0,
        le=100.0,
        description="Combined routine and IAQ exposure reduction percentage",
    )
    annual_co2_kg_saved: float = Field(
        default=1800.0,
        ge=0.0,
        description="Annual avoided CO2 emissions in kg",
    )
    num_household_members: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Count of individuals residing in household",
    )


@router.post("/calculate", response_model=ImpactMetrics, summary="Calculate personalized lung particulate dosage avoided")
def calculate_impact(payload: ImpactCalculationRequest) -> ImpactMetrics:
    """Compute direct personal health metrics, prevented PM2.5 lung mass, and equivalent cigarettes avoided.

    Args:
        payload: Parameters for dosimetry calculation.

    Returns:
        ImpactMetrics: Calculated daily/annual metrics.
    """
    return calculate_personal_impact(
        baseline_aqi=payload.baseline_aqi,
        exposure_reduction_pct=payload.exposure_reduction_pct,
        annual_co2_kg_saved=payload.annual_co2_kg_saved,
        num_household_members=payload.num_household_members,
    )
