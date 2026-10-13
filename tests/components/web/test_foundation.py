"""Tests fuer render_foundation_css() — die responsive Schicht der Web-Foundation."""

from __future__ import annotations

import re

import pytest

from mn_design_system.components.web.foundation import (
    css_font_stack,
    render_foundation_css,
)
from mn_design_system.tokens import get


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


from mn_design_system.components.web.foundation import (
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


# --- v0.16.0: Stufe display + css_font_stack ---------------------------------------------


def _mobil_block(css: str) -> str:
    """Der Text hinter ``@media (max-width: <bp-mobile>)`` bis zum Ende."""
    return css.split(f"@media (max-width: {get('web.layout.bp-mobile')})", 1)[1]


def test_display_wird_mobil_zur_desktop_h1():
    """display tritt mobil eine Stufe zurueck — auf den Desktop-Wert von h1 (Design §9).
    Der Wert kommt aus dem Token, nicht aus einem Literal."""
    mobil = _mobil_block(render_foundation_css())
    wert = re.search(r"--web-text-display:\s*([^;]+);", mobil)
    assert wert is not None, "keine Mobil-Stufe fuer display"
    assert wert.group(1).strip() == get("web.text.h1")


def test_display_wandert_nur_mobil():
    """Weder Tablet noch Desktop ueberschreiben display."""
    css = render_foundation_css()
    vor_mobil = css.split(f"@media (max-width: {get('web.layout.bp-mobile')})", 1)[0]
    assert "--web-text-display" not in vor_mobil


def test_css_font_stack_sans():
    assert css_font_stack("sans") == (
        '"Geist", system-ui, -apple-system, BlinkMacSystemFont, sans-serif'
    )


def test_css_font_stack_serif_editorial():
    assert css_font_stack("serif-editorial") == '"Source Serif 4", Georgia, serif'


def test_css_font_stack_mono():
    assert css_font_stack("mono") == (
        '"JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace'
    )


@pytest.mark.parametrize("art", ["sans", "serif-editorial", "mono"])
def test_css_font_stack_folgt_den_tokens(art):
    """Familie und Rueckfallkette kommen aus den Tokens, nicht aus dem Helfer."""
    assert css_font_stack(art) == (
        f'"{get(f"web.font.{art}")}", {get(f"web.font.stack.{art}")}'
    )


def test_css_font_stack_unbekannte_art_bricht_laut_ab():
    with pytest.raises(KeyError, match="display"):
        css_font_stack("display")


def test_css_font_stack_exportiert():
    from mn_design_system.components import web

    assert web.css_font_stack is css_font_stack
    assert "css_font_stack" in web.__all__


def test_display_mobil_folgt_dem_h1_token_nicht_einem_literal(monkeypatch):
    """Aendert sich web.text.h1, zieht die Mobil-Stufe von display mit."""
    from mn_design_system.components.web import foundation

    echtes_get = foundation.get
    monkeypatch.setattr(
        foundation,
        "get",
        lambda key, *a: "99px" if key == "web.text.h1" else echtes_get(key, *a),
    )
    mobil = _mobil_block(foundation.render_foundation_css())
    assert "--web-text-display: 99px" in mobil
