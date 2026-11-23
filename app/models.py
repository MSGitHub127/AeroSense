"""SQLAlchemy ORM models and Pydantic schemas with complete field documentation."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class VulnerabilityTier(StrEnum):
    """Health vulnerability severity tier."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class HomeType(StrEnum):
    """Dwelling architectural structure."""

    APARTMENT = "apartment"
    DETACHED_HOUSE = "detached_house"
    TOWNHOME = "townhome"
    CONDO = "condo"


class CookingFuel(StrEnum):
    """Primary kitchen cooking fuel source."""

    GAS = "natural_gas"
    INDUCTION = "induction"
    ELECTRIC = "electric_coil"
    BIOMASS = "biomass_wood"


class CommuteMode(StrEnum):
    """Primary transport mode for daily commute."""

    WALKING = "walking"
    CYCLING = "cycling"
    PUBLIC_TRANSIT = "public_transit"
    CAR_SOLO = "car_solo"
    CARPOOL = "carpool"
    EV = "electric_vehicle"


# --- SQLAlchemy ORM Tables ---


class FamilyProfileRecord(Base):
    """Database record storing encrypted family air quality profile details."""

    __tablename__ = "family_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), nullable=False, index=True)
    household_name = Column(String(120), nullable=False)
    location_city = Column(String(120), nullable=False, index=True)
    home_type = Column(String(50), nullable=False, default="apartment")
    estimated_baseline_aqi = Column(Integer, nullable=False, default=180)
    encrypted_details = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    actions = relationship("AvertedActionRecord", back_populates="profile", cascade="all, delete-orphan")


class AvertedActionRecord(Base):
    """Database record tracking specific household air actions and calculated emission metrics."""

    __tablename__ = "averted_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("family_profiles.id"), nullable=False, index=True)
    action_type = Column(String(80), nullable=False)
    pm25_avoided_ug = Column(Float, nullable=False, default=0.0)
    co2_saved_kg = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    profile = relationship("FamilyProfileRecord", back_populates="actions")


# --- Pydantic Schemas ---


class FamilyProfileRequest(BaseModel):
    """User input payload capturing household characteristics and vulnerability factors."""

    household_name: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Household or family identifier name",
    )
    location_city: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="City or metropolitan region for localized diurnal smog patterns",
    )
    home_type: HomeType = Field(
        default=HomeType.APARTMENT,
        description="Residential dwelling structure type",
    )
    cooking_fuel: CookingFuel = Field(
        default=CookingFuel.GAS,
        description="Primary stove or cooking fuel utilized indoors",
    )
    commute_mode: CommuteMode = Field(
        default=CommuteMode.CAR_SOLO,
        description="Primary mode of transportation used for daily work/school transit",
    )
    has_hepa_purifier: bool = Field(
        default=False,
        description="Whether the home operates a motorized HEPA air purifier",
    )
    vulnerable_members: list[str] = Field(
        default_factory=list,
        description="Vulnerable demographic groups present in household (e.g. infants, asthmatics, elderly, pets)",
    )
    baseline_aqi: int | None = Field(
        default=None,
        ge=0,
        le=1000,
        description="Current ambient AQI if known; defaults to regional winter estimate",
    )


class DiurnalAQIWindow(BaseModel):
    """Hourly ambient air quality period with safe activity recommendations."""

    time_range: str = Field(..., description="Clock time interval (e.g. '06:00 - 09:00')")
    predicted_pm25: float = Field(..., description="Estimated particulate matter PM2.5 in µg/m³")
    aqi_category: str = Field(..., description="Health advisory tier (e.g. Moderate, Unhealthy, Hazardous)")
    recommended_activities: list[str] = Field(..., description="Safe activities permissible during this time")
    activities_to_avoid: list[str] = Field(..., description="High-risk outdoor exposures to defer")


class RoutineRecommendation(BaseModel):
    """Personalized timing shift for common daily routines to minimize lung exposure."""

    activity_name: str = Field(..., description="Name of daily activity (commute, exercise, school run)")
    standard_time: str = Field(..., description="Typical default timing")
    optimized_time: str = Field(..., description="Air-quality optimized scheduling window")
    reasoning: str = Field(..., description="Micro-meteorological and atmospheric inversion justification")
    pm25_exposure_saved_pct: float = Field(..., description="Percentage reduction in inhaled particulates")


class DailyRoutinesResponse(BaseModel):
    """Coordinated set of low-emission daily routines tailored to ambient smog curves."""

    diurnal_windows: list[DiurnalAQIWindow] = Field(..., description="Diurnal smog distribution across 24 hours")
    commute_routine: RoutineRecommendation = Field(..., description="Optimized morning and evening travel window")
    school_routine: RoutineRecommendation = Field(..., description="Children dropoff/pickup protective protocol")
    exercise_routine: RoutineRecommendation = Field(..., description="Cardiovascular workout schedule adjustment")
    ventilation_routine: RoutineRecommendation = Field(..., description="Optimal window flush timing")
    overall_daily_exposure_reduction_pct: float = Field(..., description="Aggregate reduction in daily lung particulate dose")


class IAQHackItem(BaseModel):
    """Practical, high-yield indoor air quality intervention."""

    hack_name: str = Field(..., description="Title of the indoor air hack")
    category: str = Field(..., description="Category: filtration, kitchen, ventilation, humidity, or plants")
    difficulty: str = Field(..., description="Implementation difficulty: Easy, Moderate, or Advanced")
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD")
    pm25_reduction_pct: float = Field(..., description="Percentage reduction in indoor particulate concentrations")
    step_by_step_instructions: list[str] = Field(..., description="Actionable execution steps")
    equipment_needed: list[str] = Field(..., description="Required household materials or hardware")


class IAQHacksResponse(BaseModel):
    """Collection of high-impact indoor air interventions."""

    hacks: list[IAQHackItem] = Field(..., description="Structured list of indoor air hacks")
    room_priority_order: list[str] = Field(..., description="Rooms ranked by protective urgency")
    instant_action_tips: list[str] = Field(..., description="Zero-cost immediate interventions for today")


class SustainableAlternative(BaseModel):
    """Clean lifestyle substitution with quantified direct emission offsets."""

    habit_category: str = Field(..., description="Category: transit, heating, cooking, or waste")
    current_habit: str = Field(..., description="Current standard polluting practice")
    recommended_alternative: str = Field(..., description="Clean low-emission sustainable replacement")
    annual_co2_kg_saved: float = Field(..., description="Avoided greenhouse gas emissions in kilograms of CO2")
    local_pm25_averted_grams: float = Field(..., description="Avoided ground-level fine particulates in grams")
    cost_implication: str = Field(..., description="Financial comparison (e.g. net savings or payback)")
    implementation_guide: str = Field(..., description="Practical onboarding instructions")


class AlternativesResponse(BaseModel):
    """Comprehensive suite of sustainable household alternatives."""

    alternatives: list[SustainableAlternative] = Field(..., description="List of sustainable substitutions")
    total_annual_co2_saved_kg: float = Field(..., description="Aggregate avoided carbon in kg")
    total_local_pm25_averted_grams: float = Field(..., description="Aggregate avoided ground particulate pollution in g")


class ImpactMetrics(BaseModel):
    """Quantified direct personal health and environmental impact metrics."""

    daily_pm25_lung_dose_avoided_ug: float = Field(..., description="Micrograms of PM2.5 kept out of lungs daily")
    annual_pm25_lung_dose_avoided_mg: float = Field(..., description="Milligrams of PM2.5 prevented annually")
    equivalent_cigarettes_avoided: float = Field(..., description="Passive cigarette smoke intake equivalence avoided")
    annual_co2_saved_kg: float = Field(..., description="Carbon footprint reduced in kilograms")
    respiratory_risk_reduction_pct: float = Field(..., description="Calculated decrease in acute symptom vulnerability")


class FullAirQualityAdvisoryResponse(BaseModel):
    """Complete synthesized family air quality and smog navigation plan."""

    profile_id: str = Field(..., description="Unique profile identifier")
    household_name: str = Field(..., description="Household name")
    location_city: str = Field(..., description="Location")
    current_estimated_aqi: int = Field(..., description="Baseline ambient AQI score")
    vulnerability_tier: VulnerabilityTier = Field(..., description="Household health sensitivity tier")
    routines: DailyRoutinesResponse = Field(..., description="Coordinated diurnal low-emission routines")
    iaq_hacks: IAQHacksResponse = Field(..., description="Indoor air quality interventions")
    alternatives: AlternativesResponse = Field(..., description="Sustainable lifestyle alternatives")
    impact: ImpactMetrics = Field(..., description="Quantified health and environmental metrics")
    action_plan_markdown: str = Field(..., description="Full exportable Markdown Family Air Action Plan")


class ProfileSummaryResponse(BaseModel):
    """Summary card representing an existing saved family air advisory."""

    id: str = Field(..., description="Unique profile identifier UUID")
    household_name: str = Field(..., description="Redacted household identifier")
    location_city: str = Field(..., description="Target urban municipality")
    estimated_baseline_aqi: int = Field(..., description="Baseline ambient AQI score")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")

