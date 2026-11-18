"""Unit tests for sustainable household substitutions and emissions abatement math."""
from __future__ import annotations

from app.air_quality.alternatives_engine import generate_sustainable_alternatives
from app.models import CommuteMode, CookingFuel, HomeType


def test_generate_sustainable_alternatives_car_and_gas():
    """Verify calculated savings for gasoline car commuter with gas stove."""
    res = generate_sustainable_alternatives(
        commute_mode=CommuteMode.CAR_SOLO,
        cooking_fuel=CookingFuel.GAS,
        home_type=HomeType.APARTMENT,
        city="Delhi",
    )
    assert len(res.alternatives) >= 3
    assert res.total_annual_co2_saved_kg > 1000.0
    assert res.total_local_pm25_averted_grams > 200.0

    transit_alt = next(a for a in res.alternatives if a.habit_category == "transit")
    assert "Metro" in transit_alt.recommended_alternative or "Transit" in transit_alt.recommended_alternative

    cooking_alt = next(a for a in res.alternatives if a.habit_category == "cooking")
    assert "induction" in cooking_alt.recommended_alternative.lower()


def test_biomass_cooking_substitution():
    """Verify solid biomass cooking yields heavy particulate and carbon avoidance."""
    res = generate_sustainable_alternatives(
        commute_mode=CommuteMode.WALKING,
        cooking_fuel=CookingFuel.BIOMASS,
        home_type=HomeType.DETACHED_HOUSE,
    )
    biomass_alt = next(a for a in res.alternatives if a.habit_category == "cooking")
    assert biomass_alt.annual_co2_kg_saved >= 1500.0
    assert biomass_alt.local_pm25_averted_grams >= 1000.0
