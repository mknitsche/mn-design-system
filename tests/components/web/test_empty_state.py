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
