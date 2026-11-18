"""Unit tests for indoor air quality hacks and room defense prioritization."""
from __future__ import annotations

from app.air_quality.iaq_hacks import get_curated_iaq_hacks
from app.models import CookingFuel, HomeType


def test_get_curated_iaq_hacks_structure():
    """Verify presence of core hacks including Corsi-Rosenthal and kitchen protocol."""
    res = get_curated_iaq_hacks(
        home_type=HomeType.APARTMENT,
        cooking_fuel=CookingFuel.GAS,
        has_hepa=False,
    )
    assert len(res.hacks) >= 5
    assert len(res.room_priority_order) >= 4
    assert len(res.instant_action_tips) >= 4

    hack_names = [h.hack_name for h in res.hacks]
    assert any("Corsi-Rosenthal" in name for name in hack_names)
    assert any("Back-Burner" in name for name in hack_names)
    assert any("Flush" in name for name in hack_names)
    assert any("Humidity" in name for name in hack_names)


def test_corsi_rosenthal_specifications():
    """Check Corsi-Rosenthal step-by-step instructions and MERV-13 requirement."""
    res = get_curated_iaq_hacks()
    cr_hack = next(h for h in res.hacks if "Corsi-Rosenthal" in h.hack_name)
    assert cr_hack.pm25_reduction_pct >= 80.0
    assert any("MERV-13" in eq for eq in cr_hack.equipment_needed)
    assert len(cr_hack.step_by_step_instructions) >= 5


def test_gas_cooking_warning_present():
    """Verify gas cooking fuel specifically notes NO2/benzene hazards."""
    res = get_curated_iaq_hacks(cooking_fuel=CookingFuel.GAS)
    kitchen_hack = next(h for h in res.hacks if "Back-Burner" in h.hack_name)
    assert "NO2" in kitchen_hack.hack_name
