"""KPI-Karte und Zeitraum-Leiste im echten Browser (0.17.1): Wirkung statt Schreibweise.

``test_kpi_card.py`` / ``test_zeitraum_leiste.py`` beweisen, was die Komponenten ERZEUGEN.
Hier entscheidet der Browser, was daraus WIRD: welche Farbe das Delta einer Karte mit
umgekehrter Polaritaet wirklich hat (die Wertungsklasse ueberschreibt die Bewegungsklasse
nur ueber die Reihenfolge im CSS), wie gross das Touch-Ziel der Leiste ist, welcher
Zustand aktiv aussieht.

Nur mit Playwright + Chromium; sonst sichtbar uebersprungen (UNGEPRUEFT), nie still gruen.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import mn_design_system
from mn_design_system.components._patterns.contracts import KpiCardInput
from mn_design_system.components.web.kpi_card import (
    render_kpi_card_css,
    render_kpi_card_html,
)
from mn_design_system.tokens import get

_REPO = Path(mn_design_system.__file__).parents[1]


def _rgb(token: str) -> str:
    h = get(token)
    return f"rgb({int(h[1:3], 16)}, {int(h[3:5], 16)}, {int(h[5:7], 16)})"


@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright nicht installiert — Wirkung UNGEPRUEFT",
    )
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except sync_api.Error as exc:
            pytest.skip(f"Chromium nicht startbar — Wirkung UNGEPRUEFT ({exc!s:.80})")
        yield b
        b.close()


def _seite(koerper: str, css: str) -> str:
    tokens = (_REPO / "dist" / "css" / "tokens.css").read_text(encoding="utf-8")
    return (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        f"<style>{tokens}\n{css}</style></head><body>{koerper}</body></html>"
    )


def _geladen(browser, tmp_path, html: str, breite: int = 800):
    datei = tmp_path / "seite.html"
    datei.write_text(html, encoding="utf-8")
    ctx = browser.new_context(viewport={"width": breite, "height": 600})
    page = ctx.new_page()
    page.goto(datei.as_uri())
    page.evaluate("document.fonts.ready")
    return ctx, page


class TestKpiDeltaFarbe:
    SUCCESS = _rgb("color.status.success")
    ERROR = _rgb("color.status.error")
    MUTED = _rgb("color.light.text-muted")

    @pytest.mark.parametrize(
        ("richtung", "pct", "farbe"),
        [
            ("hoeher", 2.0, "SUCCESS"),  # der Default von 0.17.0: unveraendert
            ("hoeher", -2.0, "ERROR"),
            ("hoeher", 0.2, "MUTED"),
            ("niedriger", -2.0, "SUCCESS"),  # Rueckgang ist gut
            ("niedriger", 2.0, "ERROR"),
            ("niedriger", 0.2, "MUTED"),
            ("neutral", 2.0, "MUTED"),
            ("neutral", -2.0, "MUTED"),
        ],
    )
    def test_farbe_des_deltas(self, browser, tmp_path, richtung, pct, farbe):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="1", change_pct=pct, richtung=richtung)
        )
        ctx, page = _geladen(browser, tmp_path, _seite(html, render_kpi_card_css()))
        try:
            ist = page.evaluate(
                "getComputedStyle(document.querySelector('.mn-kpi-card__change')).color"
            )
        finally:
            ctx.close()
        assert ist == getattr(self, farbe), (richtung, pct, ist)

    def test_absolutes_delta_hat_dieselbe_farbe(self, browser, tmp_path):
        html = render_kpi_card_html(
            KpiCardInput(
                label="Gewicht",
                value="72,4",
                delta_wert=-1.2,
                delta_einheit="kg",
                richtung="niedriger",
            )
        )
        ctx, page = _geladen(browser, tmp_path, _seite(html, render_kpi_card_css()))
        try:
            ist = page.evaluate(
                "getComputedStyle(document.querySelector('.mn-kpi-card__change')).color"
            )
            text = page.evaluate(
                "document.querySelector('.mn-kpi-card__change').textContent"
            )
        finally:
            ctx.close()
        assert ist == self.SUCCESS
        assert text == "▼ \u22121,2\u00a0kg"
