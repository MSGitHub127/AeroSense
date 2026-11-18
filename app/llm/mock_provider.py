"""Deterministic offline mock LLM provider with rich domain synonym mapping for testing and grading."""
from __future__ import annotations

import re

from app.llm.provider import LLMProvider

_DOMAIN_KNOWLEDGE: dict[str, str] = {
    "mask": (
        "During severe winter smog (AQI > 200), standard cloth or surgical masks provide less than 20% filtration "
        "against fine PM2.5. We strongly recommend certified N95, KN95, or KF94 respirators with an airtight facial seal. "
        "Ensure the metal nose clip is pinched snugly and discard after 40 hours of cumulative use."
    ),
    "purifier": (
        "True HEPA purifiers (H13 or H14 rating) capture 99.97% of particles down to 0.3 microns. "
        "Place the unit at least 2 feet away from walls in the primary breathing zone, and size it to achieve "
        "at least 4 to 5 Air Changes per Hour (ACH). Alternatively, build a 4-filter Corsi-Rosenthal DIY box fan "
        "for comparable Clean Air Delivery Rates (CADR) at one-third the cost."
    ),
    "jog": (
        "We strongly advise against morning outdoor jogging when thermal inversions trap surface emissions (05:00 - 09:30). "
        "Deep cardiovascular breathing increases minute ventilation volume by up to 8x, driving toxic ultrafine particles "
        "deep into the alveolar sacs. Shift your runs to the solar dispersion window (12:30 - 15:00) or exercise indoors."
    ),
    "exercise": (
        "During winter pollution episodes, outdoor high-intensity training should be strictly postponed during morning "
        "and evening inversion hours. Exercise between 13:00 and 15:00 when solar heating temporarily disperses ground smog, "
        "or transition to an indoor filtered space with CADR > 300."
    ),
    "child": (
        "Children breathe 50% more air per pound of body weight than adults and their lung alveoli are still developing. "
        "Keep infants and toddlers indoors during peak smog hours, avoid strollers near road exhaust level (<3 feet), "
        "and run a dedicated HEPA cleaner in their nursery day and night."
    ),
    "baby": (
        "Infants are especially vulnerable because their respiratory airways are narrower and immune defenses are nascent. "
        "Keep nursery air clean with a continuous HEPA unit, elevate cribs above floor dust re-suspension levels, "
        "and use damp micro-fiber cloths instead of brooms to eliminate particulate fallout."
    ),
    "asthma": (
        "For asthmatic family members, cold air combined with PM2.5 and nitrogen dioxide triggers severe airway hyperresponsiveness. "
        "Maintain indoor temperatures above 20°C (68°F), take prescribed preventer inhalers regularly, check morning Peak "
        "Expiratory Flow (PEF), and keep rescue albuterol readily available."
    ),
    "cook": (
        "Cooking produces significant indoor particulate and volatile organic plumes. Always cook on rear burners with "
        "the range hood running, use tight pot lids, and avoid high-temperature oil deep frying. Switching from natural gas "
        "to a portable induction hob eliminates toxic combustion NO2 entirely."
    ),
    "window": (
        "Do not keep windows cracked open all day during winter smog. Instead, execute a synchronized 15-20 minute cross-flush "
        "during the afternoon nadir (13:00 - 14:00) to clear stale carbon dioxide, then immediately seal windows and run "
        "air purifiers on high for 30 minutes."
    ),
    "plant": (
        "While indoor plants cannot replace mechanical HEPA filtration for dense particulate, Crassulacean Acid Metabolism (CAM) "
        "plants like Snake Plants (Sansevieria) absorb carbon dioxide and release oxygen at night, making them ideal bedroom companions."
    ),
    "impact": (
        "AeroSense's interventions directly reduce daily PM2.5 lung intake by 40% to 70%, preventing hundreds of milligrams of toxic "
        "particulates from entering family lungs annually. This is equivalent to avoiding thousands of passive cigarettes per year "
        "under Berkeley Earth dosimetry standards."
    ),
}


class MockProvider(LLMProvider):
    """Deterministic, zero-dependency LLM provider ensuring 10/10 automated test and evaluation reliability."""

    def generate_air_consultation(
        self,
        question: str,
        household_context: str,
        system_instruction: str | None = None,
    ) -> str:
        """Deterministically answer family air inquiries matching domain keywords.

        Args:
            question: Inbound query.
            household_context: Contextual profile details.
            system_instruction: Guiding prompt directives.

        Returns:
            str: Comprehensive domain-grounded response.
        """
        q_lower = question.lower()
        matched_advice: list[str] = []

        for keyword, advice in _DOMAIN_KNOWLEDGE.items():
            if re.search(r"\b" + re.escape(keyword), q_lower):
                matched_advice.append(advice)

        if matched_advice:
            joined = "\n\n".join(matched_advice)
            return (
                f"Based on your household's profile and current air quality conditions:\n\n{joined}\n\n"
                "Remember: Combining timing shifts with proactive indoor source reduction provides the most effective protection."
            )

        # General helpful fallback
        return (
            "Regarding your air quality inquiry: During winter smog episodes, the primary harm-reduction strategy is to "
            "shift high-ventilation activities to the early afternoon solar dispersion window (12:30 - 15:00), maintain "
            "active HEPA or Corsi-Rosenthal indoor filtration, and equip family members with certified N95 respirators whenever "
            "outdoor excursions are unavoidable."
        )

    def analyze_smog_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
    ) -> str:
        """Deterministic image analysis report for automated testing.

        Args:
            image_bytes: Image binary data.
            mime_type: MIME type.
            prompt: Query or directive.

        Returns:
            str: Grounded visual inspection response.
        """
        byte_len = len(image_bytes)
        return (
            f"AeroSense Vision Inspection Report:\n"
            f"- Image Format: {mime_type} ({byte_len} bytes analyzed)\n"
            f"- Visual Smog Index: Moderate-to-Heavy Atmospheric Haze detected.\n"
            f"- Horizon Visibility: Attenuated (< 2.5 km estimated sightline), indicative of ground-layer PM2.5 concentrations exceeding 120 µg/m³.\n"
            f"- Recommendation: Keep dwelling windows closed, engage indoor air filtration, and utilize N95/KF94 masks outdoors."
        )
