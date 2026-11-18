"""Abstract base interface and factory for AeroSense LLM providers."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.config import get_settings


class LLMProvider(ABC):
    """Abstract interface defining required Generative AI capabilities for AeroSense."""

    @abstractmethod
    def generate_air_consultation(
        self,
        question: str,
        household_context: str,
        system_instruction: str | None = None,
    ) -> str:
        """Provide personalized conversational advice for family air pollution questions.

        Args:
            question: Inbound query or concern from household.
            household_context: Summary of profile, AQI, vulnerability, and active hacks.
            system_instruction: Optional system instruction prompt.

        Returns:
            str: Grounded response explaining safe actions and impact.
        """
        ...

    @abstractmethod
    def analyze_smog_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
    ) -> str:
        """Perform multimodal visual inspection of outdoor sky, smog haze, or indoor air filters.

        Args:
            image_bytes: Raw binary image payload.
            mime_type: Image MIME type (e.g. image/jpeg, image/png).
            prompt: Question or directive for visual analysis.

        Returns:
            str: Visual assessment and smog severity guidance.
        """
        ...


def get_llm_provider() -> LLMProvider:
    """Factory retrieving the configured LLM provider (Gemini or deterministic Mock).

    Returns:
        LLMProvider: Active provider instance.
    """
    settings = get_settings()
    if settings.llm_provider.lower() == "gemini" and settings.gemini_api_key:
        from app.llm.gemini_provider import GeminiProvider

        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)

    from app.llm.mock_provider import MockProvider

    return MockProvider()
