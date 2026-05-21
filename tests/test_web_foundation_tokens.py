"""Tests fuer die Web-Foundation-Tokens (web.* Namespace)."""

from __future__ import annotations

from pathlib import Path

from mn_design_system.tokens import get

_TOKENS_CSS = Path(__file__).parent.parent / "dist" / "css" / "tokens.css"


def test_web_text_scale_complete():
    """Sieben-Stufen-Typo-Skala, Anker body=16px (Design §3)."""
    assert get("web.text.caption") == "12px"
    assert get("web.text.ui") == "14px"
    assert get("web.text.body") == "16px"
    assert get("web.text.lead") == "19px"
    assert get("web.text.h3") == "23px"
    assert get("web.text.h2") == "28px"
    assert get("web.text.h1") == "33px"


def test_web_leading_scale_complete():
    """Eine Zeilenhoehe je Typo-Stufe (Design §3)."""
    assert get("web.leading.body") == "1.6"
    for step in ("caption", "ui", "lead", "h3", "h2", "h1"):
        assert get(f"web.leading.{step}") is not None


def test_web_font_families():
    """Web-Schriftfamilien — getrennt von den print-orientierten font.family.*."""
    assert get("web.font.sans") == "Geist"
    assert get("web.font.serif-editorial") == "Source Serif 4"


def test_web_stroke_whole_pixels():
    """Web-Linien nur in ganzen Pixeln — kein Sub-Pixel-Blur (Design §7)."""
    assert get("web.stroke.line") == "1px"
    assert get("web.stroke.line-strong") == "2px"
    assert get("web.stroke.focus") == "2px"


def test_web_color_tokens():
    """Separator-Grau + Fokus-Ring (Design §7)."""
    assert get("web.color.separator") == "#b4bcc8"
    assert get("web.color.separator-on-dark") == "rgba(255,255,255,0.16)"
    # focus-ring ist eine Style-Dictionary-Referenz auf color.indigo.600.
    assert get("web.color.focus-ring") == "#4F46E5"


def test_web_layout_tokens():
    """Inhalts-Breite, Seiten-Einzug, Breakpoints (Design §8 / §9)."""
    assert get("web.layout.content-width") == "1024px"
    assert get("web.layout.page-inset") == "44px"
    assert get("web.layout.bp-mobile") == "640px"
    assert get("web.layout.bp-tablet") == "1024px"


def test_tokens_css_carries_web_variables():
    """Der Style-Dictionary-Build emittiert die --web-* Custom Properties."""
    css = _TOKENS_CSS.read_text(encoding="utf-8")
    assert "--web-text-body: 16px" in css
    assert "--web-stroke-line: 1px" in css
    assert "--web-color-separator: #b4bcc8" in css
    assert "--web-layout-content-width: 1024px" in css


def test_print_tokens_untouched():
    """Die print-orientierten Tokens bleiben pt-basiert — die Foundation
    ergaenzt, ersetzt nicht (Design §1)."""
    assert get("font.size.body") == "9.5pt"
    assert get("stroke.thin") == "0.5pt"
