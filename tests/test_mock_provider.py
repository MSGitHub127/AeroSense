"""Unit tests for offline deterministic MockProvider domain synonym matching."""
from __future__ import annotations

from app.llm.mock_provider import MockProvider


def test_mock_provider_keyword_matching():
    """Verify that specific queries trigger relevant peer-reviewed guidance."""
    provider = MockProvider()

    # Query 1: Masks
    res_mask = provider.generate_air_consultation("What type of mask should we buy?", "context")
    assert "N95" in res_mask or "KF94" in res_mask

    # Query 2: Purifier
    res_purifier = provider.generate_air_consultation("How does an air purifier work?", "context")
    assert "HEPA" in res_purifier or "Corsi-Rosenthal" in res_purifier

    # Query 3: Jogging
    res_jog = provider.generate_air_consultation("Can I go for a morning jog at 6 AM?", "context")
    assert "inversion" in res_jog.lower() or "jogging" in res_jog.lower()

    # Query 4: Children
    res_child = provider.generate_air_consultation("Is it safe for young children to play outside?", "context")
    assert "children" in res_child.lower() or "infants" in res_child.lower()

    # Query 5: Cooking
    res_cook = provider.generate_air_consultation("Does cooking cause pollution indoors?", "context")
    assert "burner" in res_cook.lower() or "induction" in res_cook.lower()


def test_mock_provider_image_analysis():
    """Verify deterministic image report."""
    provider = MockProvider()
    report = provider.analyze_smog_image(b"fake_bytes_123", "image/jpeg", "Check smog")
    assert "Moderate-to-Heavy Atmospheric Haze" in report
    assert "PM2.5" in report
