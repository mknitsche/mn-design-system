"""color.tier.* Token-Familie (UX-Welle v0.2, Gemini-Gate Punkt 1 + 3).

4 Tier-Familien (bibliothek/atelier/kabinett/start) x {bg, bg-soft, border, text}.
- bg-soft: Sub-Nav-Hover, abgeleitet aus bg (55% ueber Weiss) — vollwertiger
  Token (cross-media-faehig, kein color-mix im Konsumenten).
- start: referenzielles Alias auf bibliothek (Style-Dictionary-Reference).
"""

from __future__ import annotations

import re

from mn_design_system.tokens import get

_TIERS = ["bibliothek", "atelier", "kabinett", "start"]
_SLOTS = ["bg", "bg-soft", "border", "text"]
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_alle_16_tier_tokens_vorhanden():
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


def test_bg_soft_werte():
    """Gemini-Gate Punkt 1: bg-soft als Token, bg 55% ueber Weiss."""
    assert get("color.tier.bibliothek.bg-soft") == "#f7fef9"
    assert get("color.tier.atelier.bg-soft") == "#fffdf4"
    assert get("color.tier.kabinett.bg-soft") == "#fef8f8"


def test_bg_soft_heller_als_bg():
    """bg-soft ist zarter (heller) als bg — Hover < Aktiv."""
    for tier in ["bibliothek", "atelier", "kabinett"]:
        bg = get(f"color.tier.{tier}.bg")
        bg_soft = get(f"color.tier.{tier}.bg-soft")
        bg_sum = sum(int(bg[i : i + 2], 16) for i in (1, 3, 5))
        soft_sum = sum(int(bg_soft[i : i + 2], 16) for i in (1, 3, 5))
        assert soft_sum > bg_sum, f"{tier}: bg-soft nicht heller als bg"


def test_tier_text_distinct_von_bg():
    for tier in _TIERS:
        assert get(f"color.tier.{tier}.text") != get(f"color.tier.{tier}.bg")
