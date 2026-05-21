"""Tests fuer Web-Empty-State-Renderer (UX-Welle B, v0.9.0)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import EmptyStateInput, WebTier
from mn_design_system.components.web.empty_state import (
    render_empty_state_css,
    render_empty_state_html,
)


def test_html_contains_message_and_base_class():
    html = render_empty_state_html(EmptyStateInput(message="Noch nichts hier."))
    assert "mn-empty-state" in html
    assert "Noch nichts hier." in html


def test_html_escapes_message():
    html = render_empty_state_html(EmptyStateInput(message="<script>x</script>"))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_tier_modifier_present_when_tier_set():
    html = render_empty_state_html(EmptyStateInput(message="x", tier=WebTier.ATELIER))
    assert "mn-empty-state--atelier" in html


def test_no_tier_modifier_when_tier_none():
    html = render_empty_state_html(EmptyStateInput(message="x"))
    assert "mn-empty-state--" not in html


def test_css_smoke():
    css = render_empty_state_css()
    assert ".mn-empty-state" in css
    assert "{" in css and "}" in css


def test_css_uses_foundation_tokens():
    """Re-Tokenisierung: Stroke, Schriftgroesse, Schriftfamilie und Abstaende
    kommen aus der Web-Foundation."""
    css = render_empty_state_css()
    assert "var(--web-stroke-line-strong" in css
    assert "var(--web-color-separator" in css
    assert "var(--web-text-ui" in css
    assert "var(--web-leading-ui" in css
    assert "var(--web-font-sans" in css
    assert "var(--space-" in css


def test_css_tier_modifier_uses_border_token():
    """Pro Tier eine border-left-color aus der color.tier-Familie."""
    css = render_empty_state_css()
    for tier in ("bibliothek", "atelier", "kabinett", "start"):
        assert f"var(--color-tier-{tier}-border" in css


def test_css_no_print_pt_units():
    """Keine pt-Einheiten — der Empty-State ist rein web. Geprueft auf pt als
    Einheit ('pt;' / 'pt '), nicht auf das Substring 'pt' — der Komponenten-
    Name 'mn-empty-state' enthaelt es legitim."""
    css = render_empty_state_css()
    assert "pt;" not in css and "pt " not in css
