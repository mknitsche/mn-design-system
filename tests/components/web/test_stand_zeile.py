"""Stand-Zeile (0.24.0, Welle 1, Plan T6): Text, TLP, data-stand/data-takt-min, Skript fuer „veraltet“."""

from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import StandZeileInput
from mn_design_system.components.web import (
    render_foundation_css,
    render_stand_zeile_css,
    render_stand_zeile_html,
    render_stand_zeile_js,
)


def test_ohne_tlp_und_takt_die_alte_form():
    html = render_stand_zeile_html(StandZeileInput(text="Aktualisiert 14.11. 06:05"))
    assert html == '<p class="mn-stand">Aktualisiert 14.11. 06:05</p>'


def test_mit_tlp_steht_das_etikett_hinter_dem_text():
    html = render_stand_zeile_html(
        StandZeileInput(text="Aktualisiert 14.11. 06:05", tlp="AMBER")
    )
    assert re.search(
        r"Aktualisiert 14\.11\. 06:05 · <span class=\"mn-stand__tlp\">AMBER</span></p>$",
        html,
    ), html


def test_stand_und_takt_werden_zu_data_attributen():
    html = render_stand_zeile_html(
        StandZeileInput(
            text="Aktualisiert 14.11. 06:05",
            stand_iso="2026-11-14T06:05:00+01:00",
            takt_minuten=60,
        )
    )
    assert 'data-stand="2026-11-14T06:05:00+01:00"' in html
    assert 'data-takt-min="60"' in html


def test_stand_ohne_zone_wird_abgewiesen():
    with pytest.raises(ValidationError):
        StandZeileInput(text="x", stand_iso="2026-11-14T06:05:00", takt_minuten=60)


@pytest.mark.parametrize(
    "kw", [{"stand_iso": "2026-11-14T06:05:00+01:00"}, {"takt_minuten": 60}]
)
def test_stand_und_takt_nur_zusammen(kw):
    with pytest.raises(ValidationError):
        StandZeileInput(text="x", **kw)


@pytest.mark.parametrize("takt", [0, -5])
def test_takt_muss_positiv_sein(takt):
    with pytest.raises(ValidationError):
        StandZeileInput(
            text="x", stand_iso="2026-11-14T06:05:00+01:00", takt_minuten=takt
        )


def test_maskiert():
    html = render_stand_zeile_html(StandZeileInput(text="<b>x</b>", tlp="<i>R</i>"))
    assert "<b>" not in html and "<i>" not in html


def test_js_ist_klartext_ohne_innerhtml():
    js = render_stand_zeile_js()
    assert "data-takt-min" in js and "veraltet" in js
    assert (
        "innerHTML" not in js and "eval(" not in js
    )  # CSP-sauber, kein Markup aus Daten


def test_css_kein_rohwert():
    css = render_stand_zeile_css()
    ohne = re.sub(r"var\([^()]*\)", "", css)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne)
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne)
    assert "var(--web-text-caption" in css


def test_foundation_css_unveraendert_durch_stand_zeile():
    assert "mn-stand" not in render_foundation_css()
