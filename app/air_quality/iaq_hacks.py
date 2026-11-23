"""Indoor Air Quality (IAQ) actionable interventions, low-cost hacks, and DIY protocols."""
from __future__ import annotations

from app.models import CookingFuel, HomeType, IAQHackItem, IAQHacksResponse


def _build_corsi_rosenthal_hack(has_hepa: bool) -> IAQHackItem:
    """Construct Corsi-Rosenthal box fan filtration hack specification."""
    diy_cost = 55.0 if not has_hepa else 40.0
    return IAQHackItem(
        hack_name="Corsi-Rosenthal DIY Box Fan Air Cleaner",
        category="filtration",
        difficulty="Moderate",
        estimated_cost_usd=diy_cost,
        pm25_reduction_pct=82.5,
        step_by_step_instructions=[
            "Obtain a standard 20x20 inch box fan and four MERV-13 furnace filters (20x20x1 or 20x20x2 inch).",
            "Form an open cube using the four MERV-13 filters with airflow arrows pointing inward toward the center.",
            "Tape the filter edges together securely using duct tape or heavy masking tape to eliminate air leaks.",
            "Tape a 20x20 inch cardboard square to form the bottom base plate of the cube.",
            "Mount the box fan on top of the cube with airflow blowing outward/upward into the room.",
            "Cut a circular cardboard shroud matching the fan blade circumference and tape to the fan face to boost CFM efficiency by 40%.",
            "Operate fan on medium speed in central living area or bedroom for near-silent 600 CFM CADR filtration.",
        ],
        equipment_needed=[
            "1x 20x20 inch electric box fan",
            "4x MERV-13 furnace filters (20x20x1 or 20x20x2)",
            "1x roll heavy-duty duct tape",
            "Cardboard sheet for base plate and airflow shroud",
            "Utility scissors or box cutter",
        ],
    )


def _build_kitchen_protocol_hack(cooking_fuel: CookingFuel) -> IAQHackItem:
    """Construct kitchen back-burner and ventilation hack specification."""
    gas_extra_warning = (
        " (Critical for gas stoves to avoid NO2 and benzene buildup)"
        if cooking_fuel == CookingFuel.GAS
        else ""
    )
    return IAQHackItem(
        hack_name=f"Kitchen Back-Burner & Lidded Cooking Protocol{gas_extra_warning}",
        category="kitchen",
        difficulty="Easy",
        estimated_cost_usd=0.0,
        pm25_reduction_pct=64.0,
        step_by_step_instructions=[
            "Always cook on the rear/back burners rather than front burners; range hoods capture up to 70% more particulate plume from rear positions.",
            "Turn the exhaust hood on 2 minutes before igniting burners to establish thermal convective updraft.",
            "Keep tightly fitting lids on pots and pans to contain moisture, grease aerosols, and combustion particulate.",
            "Leave range exhaust hood running on low for 10 minutes post-cooking to evacuate lingering ultra-fine particles.",
            "If no exterior exhaust hood exists, open a rear kitchen window 2 inches with a small desk fan pointing outward.",
        ],
        equipment_needed=[
            "Existing kitchen range hood or exhaust fan",
            "Tight-fitting cookware lids",
            "Optional desk fan if hood is recirculating only",
        ],
    )


def _build_solar_flush_hack() -> IAQHackItem:
    """Construct synchronized midday solar flush hack specification."""
    return IAQHackItem(
        hack_name="Synchronized Solar Midday Air Flush",
        category="ventilation",
        difficulty="Easy",
        estimated_cost_usd=0.0,
        pm25_reduction_pct=45.0,
        step_by_step_instructions=[
            "Monitor local hourly AQI curves and identify the afternoon trough (typically between 12:45 PM and 14:15 PM).",
            "Open opposing windows on opposite sides of the home for exactly 15 to 20 minutes to purge accumulated carbon dioxide (CO2).",
            "Close all windows firmly as soon as the 20-minute mark elapses.",
            "Turn all indoor air purifiers or DIY box fans to high speed for 30 minutes following window closure to scrub incoming PM2.5.",
        ],
        equipment_needed=[
            "Smartphone timer or clock",
            "Opposing exterior windows for cross-draft airflow",
        ],
    )


def _build_perimeter_sealing_hack() -> IAQHackItem:
    """Construct perimeter door sweep and weatherstripping hack specification."""
    return IAQHackItem(
        hack_name="Perimeter Infiltration Sweep & Draft Blocking",
        category="filtration",
        difficulty="Easy",
        estimated_cost_usd=18.0,
        pm25_reduction_pct=34.0,
        step_by_step_instructions=[
            "Inspect front entry door, balcony doors, and window sills using a flashlight or incense stick to identify air drafts.",
            "Install a flexible silicone under-door draft stopper or slide a twin door-sweep cushion under the front threshold.",
            "Apply self-adhesive V-strip weatherproofing foam along door jams and leaky window perimeter tracks.",
            "Keep balcony doors latched tight during evening thermal inversion hours (18:00 - 09:00).",
        ],
        equipment_needed=[
            "1x silicone door bottom seal or draft stopper",
            "1x roll self-adhesive foam weatherstripping tape",
            "Scissors and cleaning cloth",
        ],
    )


def _build_humidity_shield_hack() -> IAQHackItem:
    """Construct winter relative humidity target hack specification."""
    return IAQHackItem(
        hack_name="Winter 40-50% Relative Humidity Shield",
        category="humidity",
        difficulty="Easy",
        estimated_cost_usd=28.0,
        pm25_reduction_pct=26.0,
        step_by_step_instructions=[
            "Place a digital hygrometer in the main bedroom away from direct heat sources.",
            "Maintain indoor relative humidity between 40% and 50%; this optimal band causes suspended respirable aerosols to agglomerate and settle quickly while preserving mucous membrane barrier defense.",
            "Use distilled or reverse-osmosis (RO) water in ultrasonic humidifiers to prevent white mineral dust dispersal.",
            "If no humidifier is available, place shallow stainless steel water bowls near radiator vents or hang damp washed cotton towels.",
        ],
        equipment_needed=[
            "Digital hygrometer ($8-12)",
            "Cool-mist ultrasonic humidifier or evaporative moisture basins",
            "Distilled or filtered RO water",
        ],
    )


def _build_botanical_hack() -> IAQHackItem:
    """Construct nighttime CAM plant pairing hack specification."""
    return IAQHackItem(
        hack_name="Nighttime Crassulacean Acid Plant Pairing",
        category="plants",
        difficulty="Easy",
        estimated_cost_usd=22.0,
        pm25_reduction_pct=15.0,
        step_by_step_instructions=[
            "Place 2 potted Snake Plants (Sansevieria trifasciata) in each sleeping quarter; these perform Crassulacean Acid Metabolism (CAM), releasing oxygen and absorbing CO2 during the night.",
            "Complement with 1 Spider Plant (Chlorophytum comosum) per 100 sq ft to assist with formaldehyde and particulate trace adsorption.",
            "Wipe broad plant leaves bi-weekly with a damp cloth to remove electrostatic dust accumulation and preserve transpiration stomata.",
            "Ensure pots have proper gravel drainage to prevent root moisture and mold spore proliferation.",
        ],
        equipment_needed=[
            "2x medium Snake Plants (Sansevieria trifasciata)",
            "1x Spider Plant (Chlorophytum comosum)",
            "Well-draining pots and saucers",
        ],
    )


def get_curated_iaq_hacks(
    home_type: HomeType = HomeType.APARTMENT,
    cooking_fuel: CookingFuel = CookingFuel.GAS,
    has_hepa: bool = False,
) -> IAQHacksResponse:
    """Generate high-yield indoor air quality interventions tailored to housing type and appliances.

    Args:
        home_type: Architectural dwelling structure.
        cooking_fuel: Household cooking fuel source.
        has_hepa: Whether mechanical HEPA purifier is already operational.

    Returns:
        IAQHacksResponse: Prioritized list of actionable hacks, room priority ranking, and zero-cost tips.
    """
    hacks: list[IAQHackItem] = [
        _build_corsi_rosenthal_hack(has_hepa),
        _build_kitchen_protocol_hack(cooking_fuel),
        _build_solar_flush_hack(),
        _build_perimeter_sealing_hack(),
        _build_humidity_shield_hack(),
        _build_botanical_hack(),
    ]

    room_priority_order = [
        "Primary Bedroom (High priority: 8 hours continuous breathing zone during peak nocturnal inversion)",
        "Children / Infant Nursery (Critical priority: higher minute respiratory volume per kg body weight)",
        "Living Room / Common Gathering Space (Moderate priority: central family daytime occupancy)",
        "Home Office / Study (Moderate priority: prolonged daytime sedentary exposure)",
        "Kitchen (Activity-specific priority: active source of combustion and frying aerosols)",
        "Bathrooms & Entry Vestibule (Secondary buffer zones)",
    ]

    instant_action_tips = [
        "Switch kitchen hood fan to ON before turning on stovetops, and keep pans covered.",
        "Remove outdoor footwear at the entry threshold to prevent tracking PM2.5 and road dust onto carpets.",
        "Damp-mop hard floors instead of dry broom sweeping to avoid re-suspending settled respirable particles.",
        "Set automobile HVAC to 'Air Recirculation' mode during peak morning traffic.",
        "Keep bedroom doors closed during sleeping hours with DIY filter or HEPA unit positioned 3 feet off the floor.",
    ]

    return IAQHacksResponse(
        hacks=hacks,
        room_priority_order=room_priority_order,
        instant_action_tips=instant_action_tips,
    )
