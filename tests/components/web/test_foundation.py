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
