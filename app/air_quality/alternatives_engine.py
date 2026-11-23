"""Sustainable household lifestyle alternatives, clean fuel substitutions, and avoided emissions calculation."""
from __future__ import annotations

from app.models import AlternativesResponse, CommuteMode, CookingFuel, HomeType, SustainableAlternative


def _build_transit_alternative(commute_mode: CommuteMode, city: str) -> SustainableAlternative:
    """Build transportation alternative recommendation based on current commute mode."""
    if commute_mode in (CommuteMode.CAR_SOLO, CommuteMode.CARPOOL):
        return SustainableAlternative(
            habit_category="transit",
            current_habit="Single-occupant gasoline vehicle daily commute (approx. 25 km round-trip)",
            recommended_alternative="Electric Metro / Bus Rapid Transit (BRT) or 2-day remote work hybrid model",
            annual_co2_kg_saved=1480.0,
            local_pm25_averted_grams=420.0,
            cost_implication="Saves $1,200 - $1,800 annually on gasoline, parking fees, and vehicle maintenance",
            implementation_guide=(
                f"Integrate {city}'s rapid transit pass for Tuesday through Thursday commuting. "
                "On in-office days, walk the first/last mile with an N95 respirator during smog alerts."
            ),
        )

    return SustainableAlternative(
        habit_category="transit",
        current_habit="Active transit or bus travel along high-traffic arterial roadways",
        recommended_alternative="Greenway micromobility route selection via low-traffic residential corridors",
        annual_co2_kg_saved=210.0,
        local_pm25_averted_grams=95.0,
        cost_implication="Zero additional cost; minor routing adjustment of 5-8 minutes",
        implementation_guide=(
            "Use mapping apps set to pedestrian/bicycle modes that avoid highway corridors. "
            "Moving just 150 meters away from arterial truck routes drops acute ultrafine PM exposure by 65%."
        ),
    )


def _build_cooking_alternative(cooking_fuel: CookingFuel) -> SustainableAlternative:
    """Build culinary energy alternative recommendation based on cooking fuel."""
    if cooking_fuel == CookingFuel.GAS:
        return SustainableAlternative(
            habit_category="cooking",
            current_habit="Combustion natural gas stovetop with recirculating ventilation",
            recommended_alternative="Plug-in 1800W portable induction cooktop plate with magnetic stainless steel cookware",
            annual_co2_kg_saved=310.0,
            local_pm25_averted_grams=110.0,
            cost_implication="One-time $65 purchase of portable induction hob; lowers monthly cooking energy costs by 22%",
            implementation_guide=(
                "Place a single induction burner on the countertop for 80% of daily boiling and skillet tasks. "
                "Induction transfers 85-90% of electromagnetic energy directly to food, emitting zero combustion NO2 or particulate matter."
            ),
        )

    if cooking_fuel == CookingFuel.BIOMASS:
        return SustainableAlternative(
            habit_category="cooking",
            current_habit="Traditional solid biomass or wood-burning cooking hearth",
            recommended_alternative="Solar-buffered electric induction cooker or clean canister LPG burner",
            annual_co2_kg_saved=1850.0,
            local_pm25_averted_grams=1400.0,
            cost_implication="Subsidized clean cooking kit ($40-80); saves hundreds of hours of fuel foraging and medical inhalers",
            implementation_guide=(
                "Replace open hearth with an insulated electric hotplate or certified clean cookstove. "
                "Ventilate all remaining combustion through an elevated flue pipe chimney."
            ),
        )

    return SustainableAlternative(
        habit_category="cooking",
        current_habit="Conventional electric coil stove with long preheating cycles",
        recommended_alternative="Smart electric pressure cooker and countertop convection air fryer",
        annual_co2_kg_saved=180.0,
        local_pm25_averted_grams=35.0,
        cost_implication="Appliance pays for itself in electricity savings within 14 months",
        implementation_guide=(
            "Use sealed electric pressure cooking for pulses and stewing to reduce kitchen thermal emissions "
            "and completely contain food frying vapor."
        ),
    )


def _build_heating_alternative(home_type: HomeType) -> SustainableAlternative:
    """Build residential heating alternative recommendation based on dwelling structure."""
    if home_type in (HomeType.DETACHED_HOUSE, HomeType.TOWNHOME):
        return SustainableAlternative(
            habit_category="heating",
            current_habit="Wood-burning decorative fireplace or aging fuel-oil furnace heating",
            recommended_alternative="High-efficiency cold-climate Mini-Split Inverter Heat Pump with MERV-13 intake",
            annual_co2_kg_saved=2100.0,
            local_pm25_averted_grams=890.0,
            cost_implication="Qualifies for federal/regional clean energy heat pump rebates up to $2,000; reduces winter heating bills by 35%",
            implementation_guide=(
                "Decommission chimney dampers during winter thermal inversions. "
                "Install ductless mini-split heat pump which operates at COP 3.2+ down to -15°C."
            ),
        )

    return SustainableAlternative(
        habit_category="heating",
        current_habit="Unregulated apartment radiator or space heater with high thermal drafts",
        recommended_alternative="Smart programmable ceramic radiant panels paired with thermal blackout window drapes",
        annual_co2_kg_saved=420.0,
        local_pm25_averted_grams=75.0,
        cost_implication="$45 for thermal blackout curtains; reduces room draft heat loss by 28%",
        implementation_guide=(
            "Hang heavy insulated cellular curtains across all balcony glass and north-facing windows. "
            "Close them at dusk to trap interior heat without needing resistive blower fans that circulate dust."
        ),
    )


def _build_waste_alternative() -> SustainableAlternative:
    """Build outdoor yard and biomass waste disposal alternative recommendation."""
    return SustainableAlternative(
        habit_category="waste",
        current_habit="Open burning of autumn leaves, garden clippings, and cardboard trash",
        recommended_alternative="Neighborhood mulching compost bin and municipal yard-waste dropoff",
        annual_co2_kg_saved=380.0,
        local_pm25_averted_grams=720.0,
        cost_implication="$0 using backyard cold composting pile or city brown-bin collection",
        implementation_guide=(
            "Layer dried brown leaves with green kitchen scrap trimmings in a 3:1 ratio to generate nutrient-rich organic compost. "
            "1 single backyard leaf fire produces as much airborne carcinogenic benzo[a]pyrene as 20,000 cigarettes."
        ),
    )


def generate_sustainable_alternatives(
    commute_mode: CommuteMode = CommuteMode.CAR_SOLO,
    cooking_fuel: CookingFuel = CookingFuel.GAS,
    home_type: HomeType = HomeType.APARTMENT,
    city: str = "Metropolitan Area",
) -> AlternativesResponse:
    """Compute high-impact sustainable lifestyle substitutions tailored to household profile.

    Args:
        commute_mode: Primary mode of daily transportation.
        cooking_fuel: Fuel type for indoor culinary cooking.
        home_type: Architectural dwelling structure.
        city: Resident metropolitan area.

    Returns:
        AlternativesResponse: Calculated substitutions with quantified annual avoided CO2 and local PM2.5.
    """
    alternatives: list[SustainableAlternative] = [
        _build_transit_alternative(commute_mode, city),
        _build_cooking_alternative(cooking_fuel),
        _build_heating_alternative(home_type),
        _build_waste_alternative(),
    ]

    total_co2 = round(sum(a.annual_co2_kg_saved for a in alternatives), 1)
    total_pm25 = round(sum(a.local_pm25_averted_grams for a in alternatives), 1)

    return AlternativesResponse(
        alternatives=alternatives,
        total_annual_co2_saved_kg=total_co2,
        total_local_pm25_averted_grams=total_pm25,
    )
