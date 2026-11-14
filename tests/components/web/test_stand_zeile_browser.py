"""Stand-Zeile und Kachel-Raster im echten Browser (0.24.0): „veraltet“ ab dem Doppelten des Takts."""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns.contracts import KachelInput, StandZeileInput
from mn_design_system.components.web import (
    render_foundation_css,
    render_kachel_css,
    render_kachel_html,
    render_stand_zeile_css,
    render_stand_zeile_html,
    render_stand_zeile_js,
)

# Jetzt = 2026-11-14 12:00 (Berlin, +01:00)
JETZT_ISO = "2026-11-14T12:00:00+01:00"


def _seite(stand_iso: str | None, takt: int | None) -> str:
    z = render_stand_zeile_html(
        StandZeileInput(
            text="Aktualisiert", tlp="AMBER", stand_iso=stand_iso, takt_minuten=takt
        )
    )
    return z + f"<script>{render_stand_zeile_js()}</script>"


def _text(seite_laden, stand_iso, takt, jetzt=JETZT_ISO):
    ctx, page = seite_laden("", render_stand_zeile_css(), breite=390)
    try:
        page.clock.set_fixed_time(jetzt)
        page.set_content(
            f"<style>{render_stand_zeile_css()}</style>{_seite(stand_iso, takt)}"
        )
        return page.evaluate("document.querySelector('.mn-stand').textContent")
    finally:
        ctx.close()


@pytest.mark.parametrize(
    ("alter_min", "takt", "veraltet"),
    [
        (30, 60, False),
        (60, 60, False),
        (120, 60, False),  # genau das Doppelte ist noch nicht veraltet
        (121, 60, True),
        (200, 30, True),  # Heute: 30 Minuten
        (59, 30, False),
        (-30, 60, False),  # Stand in der Zukunft (Uhr-Abweichung) ist nie veraltet
    ],
)
def test_veraltet_erst_ueber_dem_doppelten_takt(seite_laden, alter_min, takt, veraltet):
    from datetime import datetime, timedelta

    jetzt = datetime.fromisoformat(JETZT_ISO)
    stand = (jetzt - timedelta(minutes=alter_min)).isoformat()
    text = _text(seite_laden, stand, takt)
    assert ("· veraltet" in text) is veraltet, text
    assert "AMBER" in text


def test_ohne_data_attribute_bleibt_die_zeile_unberuehrt(seite_laden):
    assert "veraltet" not in _text(seite_laden, None, None)


def test_unlesbarer_stand_fuegt_nichts_an(seite_laden):
    ctx, page = seite_laden("", "", breite=390)
    try:
        page.clock.set_fixed_time(JETZT_ISO)
        page.set_content(
            '<p class="mn-stand" data-stand="kaputt" data-takt-min="60">x</p>'
            f"<script>{render_stand_zeile_js()}</script>"
        )
        assert page.evaluate("document.querySelector('.mn-stand').textContent") == "x"
    finally:
        ctx.close()


def test_zweimal_laufen_haengt_nur_einmal_an(seite_laden):
    ctx, page = seite_laden("", "", breite=390)
    try:
        page.clock.set_fixed_time(JETZT_ISO)
        page.set_content(_seite("2026-11-14T06:00:00+01:00", 60))
        page.evaluate(render_stand_zeile_js())
        n = page.evaluate("document.querySelectorAll('.mn-stand__veraltet').length")
        assert n == 1
    finally:
        ctx.close()


def test_kachel_raster_eine_spalte_unten_zwei_ab_bp_tablet(seite_laden):
    kacheln = "".join(
        render_kachel_html(
            KachelInput(kicker=f"K{i}", titel_id=f"k{i}", display_zahl=str(i))
        )
        for i in range(4)
    )
    html = f'<div class="mn-kachel-raster">{kacheln}</div>'
    css = render_foundation_css() + render_kachel_css()

    def spalten(breite):
        ctx, page = seite_laden(html, css, breite=breite)
        try:
            return page.evaluate(
                "new Set([...document.querySelectorAll('.mn-kachel')].map(k => Math.round(k.getBoundingClientRect().left))).size"
            )
        finally:
            ctx.close()

    assert spalten(390) == 1
    assert spalten(1023) == 1
    assert spalten(1024) == 2
    assert spalten(1400) == 2
