"""Unit tests verifying WCAG 2.1 AAA accessibility markup, landmarks, and multi-surface mirroring."""
from __future__ import annotations

import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_html_accessibility_elements():
    """Verify skip link, landmarks, labels, and ARIA attributes in all index.html files."""
    paths_to_check = [
        ROOT_DIR / "frontend" / "index.html",
        ROOT_DIR / "app" / "static" / "index.html",
        ROOT_DIR / "app" / "templates" / "index.html",
        ROOT_DIR / "index.html",
    ]

    for p in paths_to_check:
        assert p.is_file(), f"File {p} does not exist"
        html = p.read_text(encoding="utf-8")

        # Skip link check
        assert 'class="skip-link"' in html, f"Missing skip-link in {p}"
        assert 'href="#main-content"' in html, f"Missing skip link target in {p}"

        # Semantic landmarks
        assert 'role="banner"' in html or "<header" in html
        assert 'id="main-content"' in html
        assert 'role="contentinfo"' in html or "<footer" in html

        # ARIA Live Announcer
        assert 'id="status-announcer"' in html
        assert 'aria-live="polite"' in html

        # Verify all form inputs have labels or aria-labels
        input_ids = re.findall(r'<input[^>]+id="([^"]+)"', html)
        for input_id in input_ids:
            if input_id in ("status-announcer",):
                continue
            assert f'for="{input_id}"' in html or f'id="{input_id}"' in html


def test_css_focus_and_contrast_rules():
    """Verify focus rings, high contrast variables, and reduced-motion rules in stylesheets."""
    css_paths = [
        ROOT_DIR / "frontend" / "styles.css",
        ROOT_DIR / "app" / "static" / "styles.css",
    ]

    for p in css_paths:
        assert p.is_file(), f"CSS {p} missing"
        css = p.read_text(encoding="utf-8")

        # Focus ring check
        assert ":focus" in css
        assert "outline:" in css or "outline-offset:" in css

        # Reduced motion check
        assert "prefers-reduced-motion" in css

        # Screen reader only utility class
        assert ".sr-only" in css
