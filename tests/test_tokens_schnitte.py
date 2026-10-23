"""v0.16.0: Schnitt-Tokens, Web-Schriftketten und die Stufe display (claudeAI TODO-887).

Hintergrund: Die Verwender (claudeAI) trugen Schnittnamen („Geist-Bold“, „JetBrainsMono-Bold“,
„SourceSerif-BoldItalic“) und Web-Rueckfallketten als Literale in eigenen Tabellen — ein
Schriftwechsel im Design-System zog dort nicht nach. Jetzt kommen sie als Tokens aus dem
Design-System; ``tokens.py`` und ``dist/*`` entstehen per ``npm run build`` und werden nie
von Hand bearbeitet.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from reportlab.pdfbase import pdfmetrics

from mn_design_system.fonts import font_path, register_all_fonts
from mn_design_system.helpers import font_family
from mn_design_system.tokens import TOKENS, get

_DIST = Path(__file__).parent.parent / "dist"
ROOT_PAKET = Path(__file__).parent.parent / "mn_design_system"

#: Token-Schluessel (ohne ``font.family.``) -> Schriftname.
_SCHNITTE = {
    "sans-bold": "Geist-Bold",
    "sans-medium": "Geist-Medium",
    "sans-light": "Geist-Light",
    "mono-bold": "JetBrainsMono-Bold",
    "italic-editorial-bold": "SourceSerif4-BoldItalic",
}


@pytest.fixture(autouse=True)
def _register_fonts():
    register_all_fonts()


@pytest.mark.parametrize(("token", "name"), sorted(_SCHNITTE.items()))
def test_schnitt_token_traegt_den_schriftnamen(token, name):
    assert font_family(token) == name


@pytest.mark.parametrize("token", sorted(_SCHNITTE))
def test_schnitt_token_ist_ein_angemeldeter_schriftname(token):
    """Ein Token, dessen Name ReportLab nicht kennt, faellt erst beim Rendern als
    ValueError auf (so geschehen mit italic-editorial bis 0.14.2)."""
    assert pdfmetrics.getFont(font_family(token)) is not None
    assert font_path(font_family(token)) is not None, "Name ohne Datei im Paket"


def test_zitat_schnitte_zeigen_auf_dieselbe_datei_wie_die_kurznamen():
    assert font_path(font_family("italic-editorial-bold")) == font_path(
        "SourceSerif-BoldItalic"
    )
    assert font_path(font_family("italic-editorial")) == font_path("SourceSerif-Italic")


# --- Web-Tokens ------------------------------------------------------------------------


def test_web_mono_und_rueckfallketten():
    assert get("web.font.mono") == "JetBrains Mono"
    assert get("web.font.stack.sans") == (
        "system-ui, -apple-system, BlinkMacSystemFont, sans-serif"
    )
    assert get("web.font.stack.serif-editorial") == "Georgia, serif"
    assert get("web.font.stack.mono") == ('ui-monospace, "SF Mono", Menlo, monospace')


def test_stufe_display_ist_die_groesste_der_skala():
    assert get("web.text.display") == "40px"
    assert get("web.leading.display") == "1.1"
    stufen = ["caption", "ui", "body", "lead", "h3", "h2", "h1", "display"]
    px = [int(get(f"web.text.{s}").removesuffix("px")) for s in stufen]
    assert px == sorted(set(px)), "die Skala muss streng aufsteigen"


# --- Build-Artefakte: aus tokens/*.json erzeugt, nie von Hand --------------------------


def test_dist_json_stimmt_mit_tokens_py_ueberein():
    """tokens.py und dist/json werden vom selben Build erzeugt; eine Abweichung heisst,
    eine der beiden Dateien wurde von Hand bearbeitet oder der Build lief nicht."""
    dist = json.loads((_DIST / "json" / "tokens.json").read_text(encoding="utf-8"))
    assert dist == TOKENS


def test_css_traegt_die_neuen_variablen():
    css = (_DIST / "css" / "tokens.css").read_text(encoding="utf-8")
    assert "--web-text-display: 40px" in css
    assert "--web-leading-display: 1.1" in css
    # Familiennamen mit Ziffer/Leerzeichen muessen in CSS gequotet sein ("Source Serif 4" ist
    # ungequotet kein gueltiger Name; var()-Rueckfaelle griffen dann nie).
    assert '--web-font-mono: "JetBrains Mono"' in css
    assert '--web-font-serif-editorial: "Source Serif 4"' in css
    assert '--web-font-sans: "Geist"' in css
    assert (
        "--web-font-stack-sans: system-ui, -apple-system, BlinkMacSystemFont, "
        "sans-serif" in css
    )
    assert "--web-font-stack-serif-editorial: Georgia, serif" in css
    assert '--web-font-stack-mono: ui-monospace, "SF Mono", Menlo, monospace' in css
    assert "--font-family-sans-bold: Geist-Bold" in css
    assert "--font-family-italic-editorial-bold: SourceSerif4-BoldItalic" in css


def test_latex_traegt_die_neuen_token():
    tex = (ROOT_PAKET / "latex" / "mn-design.sty").read_text(encoding="utf-8")
    assert (
        r"\csname mn@token@font.family.mono-bold\endcsname{JetBrainsMono-Bold}" in tex
    )
    assert (
        r"\csname mn@token@font.family.italic-editorial-bold\endcsname{SourceSerif4-BoldItalic}"
        in tex
    )
