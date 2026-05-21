"""color.diagram.* — schaltbare kategorische Diagramm-Palette (v0.12.0).

KT-1 S260, Welle-3 Farb-Harmonie. 12 unterscheidbare Hues fuer UNGEORDNETE
Diagramm-Kategorien (EAM-Schichten, Architektur-Knoten-Rollen, Skill-Typen).

Methode: perzeptueller OKLCH-Ring, 12 Hues alle 30 Grad, indigo-verankert.
Jede Kategorie hat base (Linien/Rahmen/Text) + nuance (helle Fuellung) +
dark (Text auf Nuance). Zwei Varianten hinterlegt — vivid (aktiv) und uniform —
umschaltbar per Config-Edit (Referenz-Redirect der 36 semantischen Tokens).

Drift-Schutz:
- alle 36 semantischen Tokens vorhanden + valides Hex
- VIVID ist die aktive Variante (Default-Aufloesung trifft die vivid-Tabelle)
- WCAG-AA: base-auf-Weiss >=3:1, base-auf-Nuance >=3:1, dark-auf-Nuance >=4.5:1
- indigo-Anker: diagram.indigo entspricht der vivid-indigo-Speiche
"""

from __future__ import annotations

import re

from mn_design_system.tokens import get

_HUES = [
    "crimson",
    "copper",
    "amber",
    "citron",
    "green",
    "emerald",
    "teal",
    "azure",
    "blue",
    "indigo",
    "violet",
    "magenta",
]
_SLOTS = ["base", "nuance", "dark"]
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_WHITE = "#ffffff"


def _rl(hex_str: str) -> float:
    """WCAG 2.1 relative Luminanz."""
    h = hex_str.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))

    def lin(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _ratio(a: str, b: str) -> float:
    la, lb = _rl(a), _rl(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def test_alle_36_diagram_tokens_vorhanden():
    for hue in _HUES:
        for slot in _SLOTS:
            key = f"color.diagram.{hue}.{slot}"
            assert get(key) is not None, f"Token fehlt: {key}"


def test_alle_diagram_tokens_sind_valides_hex():
    for hue in _HUES:
        for slot in _SLOTS:
            val = get(f"color.diagram.{hue}.{slot}")
            assert _HEX.match(val), f"color.diagram.{hue}.{slot} kein Hex: {val}"


def test_interne_variant_tabellen_nicht_im_build_output():
    """_variant_* sind _meta-Prefix-Tabellen — duerfen nicht im Output landen."""
    assert get("color.diagram._variant_vivid.crimson.base") is None
    assert get("color.diagram._variant_uniform.crimson.base") is None
    assert get("color.diagram._variant") is None


def test_vivid_ist_aktive_variante():
    """Default-Aufloesung trifft die VIVID-Tabelle (KT-1-Default S260)."""
    # Stichprobe: vivid-crimson-base ist #ef1e6e, uniform waere #bb6a7b.
    assert get("color.diagram.crimson.base") == "#ef1e6e"
    assert get("color.diagram.magenta.base") == "#dd1ebd"
    assert get("color.diagram.indigo.base") == "#6c73f9"


def test_indigo_anker():
    """diagram.indigo ist die indigo-verankerte Speiche (Hue 276.97 Grad)."""
    # vivid-indigo-base; indigo-600 (#4F46E5) dient separat als dark-Variante.
    assert get("color.diagram.indigo.base") == "#6c73f9"
    assert get("color.diagram.indigo.dark") == "#3812c1"


def test_wcag_base_auf_weiss():
    """base-Ton auf Weiss >=3:1 (grafischer Kontrast — Linien/Rahmen)."""
    for hue in _HUES:
        base = get(f"color.diagram.{hue}.base")
        r = _ratio(base, _WHITE)
        assert r >= 3.0, f"diagram.{hue}.base auf Weiss nur {r:.2f}:1 (<3:1)"


def test_wcag_base_auf_eigener_nuance():
    """base-Ton auf eigener Nuance >=3:1 (grafischer Kontrast)."""
    for hue in _HUES:
        base = get(f"color.diagram.{hue}.base")
        nuance = get(f"color.diagram.{hue}.nuance")
        r = _ratio(base, nuance)
        assert r >= 3.0, f"diagram.{hue} base/nuance nur {r:.2f}:1 (<3:1)"


def test_wcag_dark_auf_eigener_nuance():
    """dark-Ton auf eigener Nuance >=4.5:1 (Kleintext — Labels)."""
    for hue in _HUES:
        dark = get(f"color.diagram.{hue}.dark")
        nuance = get(f"color.diagram.{hue}.nuance")
        r = _ratio(dark, nuance)
        assert r >= 4.5, f"diagram.{hue} dark/nuance nur {r:.2f}:1 (<4.5:1)"


def test_base_toene_paarweise_unterscheidbar():
    """Die 12 base-Toene sind alle verschieden (kategoriale Trennung)."""
    bases = [get(f"color.diagram.{h}.base") for h in _HUES]
    assert len(set(bases)) == 12, "diagram base-Toene nicht alle eindeutig"
