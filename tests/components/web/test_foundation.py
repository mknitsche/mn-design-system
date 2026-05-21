"""Tests fuer render_foundation_css() — die responsive Schicht der Web-Foundation."""

from __future__ import annotations

from mn_design_system.components.web.foundation import render_foundation_css


def test_mobile_breakpoint_present():
    """< bp-mobile (640px): Seiten-Einzug schrumpft auf 16px (Design §9)."""
    css = render_foundation_css()
    assert "@media (max-width: 640px)" in css
    assert "--web-layout-page-inset: 16px" in css


def test_tablet_breakpoint_present():
    """640-1024px: Seiten-Einzug 32px (Design §9)."""
    css = render_foundation_css()
    assert "@media (max-width: 1024px)" in css
    assert "--web-layout-page-inset: 32px" in css


def test_display_sizes_step_down_on_mobile():
    """Display-Stufen treten auf mobile einen Schritt zurueck (Design §9)."""
    css = render_foundation_css()
    assert "--web-text-h1: 27px" in css
    assert "--web-text-h2: 24px" in css
    assert "--web-text-h3: 21px" in css


def test_reading_anchors_stay_static():
    """body/ui/caption/lead sind Lese-Anker — sie duerfen nie responsiv wandern."""
    css = render_foundation_css()
    assert "--web-text-body" not in css
    assert "--web-text-ui" not in css
    assert "--web-text-caption" not in css
    assert "--web-text-lead" not in css


def test_exported_from_web_package():
    """render_foundation_css ist aus mn_design_system.components.web importierbar."""
    from mn_design_system.components.web import render_foundation_css as exported

    assert exported is render_foundation_css


from mn_design_system.components.web.foundation import (  # noqa: E402
    render_initiale_css,
)


def test_initiale_dropcap_uses_initial_letter():
    """Drop-Cap per initial-letter, mit @supports-Fallback auf float (Design §4)."""
    css = render_initiale_css()
    assert "initial-letter: 2" in css
    assert "@supports not (initial-letter: 2)" in css
    assert "float: left" in css


def test_initiale_uses_editorial_serif():
    css = render_initiale_css()
    assert "var(--web-font-serif-editorial" in css
    assert "font-style: italic" in css


def test_initiale_wort_form_present():
    """Spielform 2 — Wort-Initiale, erstes Wort 1,3x auf der Grundlinie."""
    css = render_initiale_css()
    assert ".mn-initiale-wort" in css
    assert "font-size: 1.3em" in css


def test_initiale_exported_from_web_package():
    from mn_design_system.components.web import render_initiale_css as exported

    assert exported is render_initiale_css
