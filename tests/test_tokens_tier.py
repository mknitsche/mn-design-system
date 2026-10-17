"""color.tier.* Token-Familie (UX-Welle v0.2, Gemini-Gate Punkt 1 + 3).

6 Tier-Familien (bibliothek/atelier/kabinett/start/observatorium/magazin) x
{bg, bg-soft, border, text}.
- bg-soft: Sub-Nav-Hover, abgeleitet aus bg (55% ueber Weiss) — vollwertiger
  Token (cross-media-faehig, kein color-mix im Konsumenten).
- start: referenzielles Alias auf bibliothek (Style-Dictionary-Reference).
- observatorium: referenzielles Alias auf atelier (AMBER-Bereich, 0.17.0).
- magazin: eigene, gedaempfte Grau-Nuance (0.17.1) — bg/border/text referenzieren die
  Grau-Skala, bg-soft und hover-on-dark sind abgeleitet.
"""

from __future__ import annotations

import re

from mn_design_system.tokens import get

_TIERS = ["bibliothek", "atelier", "kabinett", "start", "observatorium", "magazin"]
_SLOTS = ["bg", "bg-soft", "border", "text"]
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_alle_24_tier_tokens_vorhanden():
    for tier in _TIERS:
        for slot in _SLOTS:
            key = f"color.tier.{tier}.{slot}"
            assert get(key) is not None, f"Token fehlt: {key}"


def test_alle_tier_tokens_sind_valides_hex():
    for tier in _TIERS:
        for slot in _SLOTS:
            val = get(f"color.tier.{tier}.{slot}")
            assert _HEX.match(val), f"color.tier.{tier}.{slot} kein Hex: {val}"


def test_start_ist_alias_auf_bibliothek():
    """Gemini-Gate Punkt 3: start referenziert bibliothek (kein Hex-Copy)."""
    for slot in _SLOTS:
        assert get(f"color.tier.start.{slot}") == get(f"color.tier.bibliothek.{slot}")


def test_observatorium_ist_alias_auf_atelier():
    """0.17.0: observatorium referenziert atelier (AMBER-Werte unter eigenem
    Namen, wie start auf bibliothek) — alle Slots inkl. hover-on-dark gleich."""
    for slot in [*_SLOTS, "hover-on-dark"]:
        alias = get(f"color.tier.observatorium.{slot}")
        assert alias is not None, f"Token fehlt: color.tier.observatorium.{slot}"
        assert alias == get(f"color.tier.atelier.{slot}")


def test_bg_soft_werte():
    """Gemini-Gate Punkt 1: bg-soft als Token, bg 55% ueber Weiss."""
    assert get("color.tier.bibliothek.bg-soft") == "#f7fef9"
    assert get("color.tier.atelier.bg-soft") == "#fffdf4"
    assert get("color.tier.kabinett.bg-soft") == "#fef8f8"


def test_bg_soft_heller_als_bg():
    """bg-soft ist zarter (heller) als bg — Hover < Aktiv."""
    for tier in ["bibliothek", "atelier", "kabinett", "magazin"]:
        bg = get(f"color.tier.{tier}.bg")
        bg_soft = get(f"color.tier.{tier}.bg-soft")
        bg_sum = sum(int(bg[i : i + 2], 16) for i in (1, 3, 5))
        soft_sum = sum(int(bg_soft[i : i + 2], 16) for i in (1, 3, 5))
        assert soft_sum > bg_sum, f"{tier}: bg-soft nicht heller als bg"


def test_tier_text_distinct_von_bg():
    for tier in _TIERS:
        assert get(f"color.tier.{tier}.text") != get(f"color.tier.{tier}.bg")


def _luminanz(hexfarbe: str) -> float:
    r, g, b = (int(hexfarbe[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _kontrast(a: str, b: str) -> float:
    hell, dunkel = sorted((_luminanz(a), _luminanz(b)), reverse=True)
    return (hell + 0.05) / (dunkel + 0.05)


def test_magazin_ist_eine_graue_nuance_aus_der_grau_skala():
    """0.17.1: magazin ist KEIN Alias auf einen farbigen Tier, sondern bezieht bg,
    border und text aus der Grau-Skala (Lead-Entscheid: gedaempfte Grau-Nuance)."""
    assert get("color.tier.magazin.bg") == get("color.grey.50")
    assert get("color.tier.magazin.border") == get("color.grey.200")
    assert get("color.tier.magazin.text") == get("color.grey.700")


def test_magazin_ist_nicht_gleich_einem_anderen_tier():
    """Eigene Identitaet: kein Slot ist ein Duplikat der uebrigen Tiers."""
    for slot in ["bg", "border", "text"]:
        wert = get(f"color.tier.magazin.{slot}")
        assert wert is not None, f"Token fehlt: color.tier.magazin.{slot}"
        for tier in ["bibliothek", "atelier", "kabinett", "start", "observatorium"]:
            assert wert != get(f"color.tier.{tier}.{slot}"), f"magazin.{slot} == {tier}"


def test_magazin_bg_soft_ist_bg_zu_55_prozent_ueber_weiss():
    """Dieselbe Ableitung wie bei den anderen Tiers (Kopf der Datei)."""
    bg = get("color.tier.magazin.bg")
    erwartet = "#" + "".join(
        f"{round(int(bg[i : i + 2], 16) * 0.55 + 255 * 0.45):02x}" for i in (1, 3, 5)
    )
    assert get("color.tier.magazin.bg-soft") == erwartet == "#fafafa"


def test_magazin_hover_on_dark_ist_border_halbtransparent():
    """Wie bei den anderen Tiers: Tier-Glow = border mit Deckkraft 0,5."""
    border = get("color.tier.magazin.border")
    r, g, b = (int(border[i : i + 2], 16) for i in (1, 3, 5))
    assert get("color.tier.magazin.hover-on-dark") == f"rgba({r},{g},{b},0.5)"


def test_magazin_text_hat_lesbaren_kontrast():
    """WCAG 1.4.3: Text >= 4,5:1 auf bg (Aktiv-Pille, Chip) UND auf bg-soft
    (Sub-Nav-Hover) UND auf Weiss (Sub-Nav-Leiste)."""
    text = get("color.tier.magazin.text")
    assert _kontrast(text, get("color.tier.magazin.bg")) >= 4.5
    assert _kontrast(text, get("color.tier.magazin.bg-soft")) >= 4.5
    assert _kontrast(text, get("color.light.surface")) >= 4.5
