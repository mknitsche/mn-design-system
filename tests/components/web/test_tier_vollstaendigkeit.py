"""Jeder ``WebTier`` hat in JEDER Komponente mit eigener Tier-Liste seine Regeln.

Fuenf Komponenten fuehren eine eigene Tier-Liste (Masthead, Tier-Chip, Sub-Nav,
Content-Card, Empty-State). Ein neuer Tier ohne Eintrag dort bekaeme keine Hover- und
Aktiv-Farbe — und kein Test fiele auf, solange die Tests ihre Tier-Liste von Hand
tippen. Dieser Test leitet die Liste aus dem Enum ab und prueft die Wirkung (die Regel
steht im CSS, mit dem ECHTEN Token-Wert als ``var()``-Rueckfall), nicht die Schreibweise
einer Liste (0.18.0, Tier ``magazin``).
"""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns.contracts import WebTier
from mn_design_system.components.web.content_card import render_content_card_css
from mn_design_system.components.web.empty_state import render_empty_state_css
from mn_design_system.components.web.masthead import render_masthead_css
from mn_design_system.components.web.sub_nav import render_sub_nav_css
from mn_design_system.components.web.tier_chip import render_tier_chip_css
from mn_design_system.tokens import get

_TIERS = [t.value for t in WebTier]


def test_untergrenze_alle_tiers_sind_da():
    """LP-36: eine leere Enum-Ableitung wuerde jeden Test unten trivial bestehen."""
    assert len(_TIERS) >= 6
    assert "magazin" in _TIERS


@pytest.mark.parametrize("tier", _TIERS)
def test_masthead_pille_und_chip(tier):
    css = render_masthead_css()
    assert f".mn-masthead__pill--{tier}:not(.is-active):hover" in css
    assert f".mn-masthead__pill--{tier}.is-active" in css
    assert f".mn-masthead__chip--{tier}" in css
    hover = get(f"color.tier.{tier}.hover-on-dark")
    bg = get(f"color.tier.{tier}.bg")
    text = get(f"color.tier.{tier}.text")
    assert f"var(--color-tier-{tier}-hover-on-dark, {hover})" in css
    assert f"var(--color-tier-{tier}-bg, {bg})" in css
    assert f"var(--color-tier-{tier}-text, {text})" in css


@pytest.mark.parametrize("tier", _TIERS)
def test_tier_chip(tier):
    css = render_tier_chip_css()
    assert f".mn-tier-chip--{tier} " in css or f".mn-tier-chip--{tier}{{" in css
    assert f".mn-tier-chip--{tier}.mn-tier-chip--bordered" in css
    assert f"var(--color-tier-{tier}-border" in css


@pytest.mark.parametrize("tier", _TIERS)
def test_sub_nav(tier):
    css = render_sub_nav_css()
    assert f".mn-sub-nav--{tier} .mn-sub-nav__tab:not(.is-active):hover" in css
    assert f".mn-sub-nav--{tier} .mn-sub-nav__tab.is-active" in css
    for slot in ("bg", "border", "text"):
        wert = get(f"color.tier.{tier}.{slot}")
        assert f"var(--color-tier-{tier}-{slot}, {wert})" in css


@pytest.mark.parametrize("tier", _TIERS)
def test_content_card(tier):
    css = render_content_card_css()
    border = get(f"color.tier.{tier}.border")
    assert f".mn-content-card--{tier} " in css
    assert f"var(--color-tier-{tier}-border, {border})" in css


@pytest.mark.parametrize("tier", _TIERS)
def test_empty_state(tier):
    css = render_empty_state_css()
    assert f".mn-empty-state--{tier} " in css
    assert f"var(--color-tier-{tier}-border" in css
