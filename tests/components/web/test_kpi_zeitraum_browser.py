"""KPI-Karte und Zeitraum-Leiste im echten Browser (0.18.0): Wirkung statt Schreibweise.

``test_kpi_card.py`` / ``test_zeitraum_leiste.py`` beweisen, was die Komponenten ERZEUGEN.
Hier entscheidet der Browser, was daraus WIRD: welche Farbe das Delta einer Karte mit
umgekehrter Polaritaet wirklich hat (die Wertungsklasse ueberschreibt die Bewegungsklasse
nur ueber die Reihenfolge im CSS), wie gross das Touch-Ziel der Leiste ist, welcher
Zustand aktiv aussieht und ob die Leiste ohne Skript navigiert.

Nur mit Playwright + Chromium; sonst sichtbar uebersprungen (UNGEPRUEFT), nie still gruen.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import mn_design_system
from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    ZeitraumLeisteInput,
    ZeitraumOption,
)
from mn_design_system.components.web.kpi_card import (
    render_kpi_card_css,
    render_kpi_card_html,
)
from mn_design_system.components.web.zeitraum_leiste import (
    render_zeitraum_leiste_css,
    render_zeitraum_leiste_html,
)
from mn_design_system.tokens import get

_REPO = Path(mn_design_system.__file__).parents[1]


def _rgb(token: str) -> str:
    h = get(token)
    return f"rgb({int(h[1:3], 16)}, {int(h[3:5], 16)}, {int(h[5:7], 16)})"


def _leiste(labels=("30 Tage", "90 Tage", "1 Jahr"), aktiv=1) -> ZeitraumLeisteInput:
    return ZeitraumLeisteInput(
        optionen=[
            ZeitraumOption(label=label, href=f"?tage={i}", active=i == aktiv)
            for i, label in enumerate(labels)
        ]
    )


def _leiste_seite(**kw) -> str:
    return _seite(
        render_zeitraum_leiste_html(_leiste(**kw)), render_zeitraum_leiste_css()
    )


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


_OPTION = ".mn-zeitraum-leiste__option"


def _stil(page, nr: int, eigenschaft: str) -> str:
    return page.evaluate(
        "([sel, nr, e]) => getComputedStyle(document.querySelectorAll(sel)[nr])[e]",
        [_OPTION, nr, eigenschaft],
    )


class TestZeitraumLeisteImBrowser:
    @pytest.mark.parametrize("breite", [320, 1000])
    def test_jede_option_ist_mindestens_44_px_gross(self, browser, tmp_path, breite):
        """Auch das kurze Label: „1 J" waere ohne min-width schmaler als ein Finger."""
        ctx, page = _geladen(
            browser,
            tmp_path,
            _leiste_seite(labels=("7", "30 Tage", "1 J")),
            breite=breite,
        )
        try:
            boxen = page.evaluate(
                "(sel) => [...document.querySelectorAll(sel)].map("
                "e => { const r = e.getBoundingClientRect();"
                " return [r.width, r.height]; })",
                _OPTION,
            )
        finally:
            ctx.close()
        assert len(boxen) == 3
        for breit, hoch in boxen:
            assert breit >= 44 and hoch >= 44, boxen

    def test_auf_dem_kleinsten_telefon_kein_seitlicher_ueberlauf(
        self, browser, tmp_path
    ):
        ctx, page = _geladen(browser, tmp_path, _leiste_seite(), breite=320)
        try:
            masse = page.evaluate(
                "() => [document.documentElement.scrollWidth,"
                " document.documentElement.clientWidth,"
                " document.querySelector('.mn-zeitraum-leiste').scrollWidth,"
                " document.querySelector('.mn-zeitraum-leiste').clientWidth]"
            )
        finally:
            ctx.close()
        assert masse[0] <= masse[1], masse  # Seite
        assert masse[2] <= masse[3], masse  # nichts in der Leiste abgeschnitten

    def test_aktiv_ruhend_und_hover(self, browser, tmp_path):
        ctx, page = _geladen(browser, tmp_path, _leiste_seite(aktiv=1))
        try:
            # ruhend: gedaempft auf Weiss
            assert _stil(page, 0, "color") == _rgb("color.light.text-muted")
            assert _stil(page, 0, "backgroundColor") == "rgba(0, 0, 0, 0)"
            # aktiv: Akzent auf Indigo-50
            assert _stil(page, 1, "color") == _rgb("color.light.accent")
            assert _stil(page, 1, "backgroundColor") == _rgb("color.indigo.50")
            # Hover auf einer ruhenden Option
            page.hover(f"{_OPTION} >> nth=0")
            assert _stil(page, 0, "color") == _rgb("color.light.text")
            assert _stil(page, 0, "backgroundColor") == _rgb(
                "color.light.surface-subtle"
            )
            # Hover auf der aktiven bleibt aktiv (Reihenfolge im CSS)
            page.hover(f"{_OPTION} >> nth=1")
            assert _stil(page, 1, "color") == _rgb("color.light.accent")
            assert _stil(page, 1, "backgroundColor") == _rgb("color.indigo.50")
        finally:
            ctx.close()

    def test_tastaturfokus_zeigt_den_ring_innen(self, browser, tmp_path):
        ctx, page = _geladen(browser, tmp_path, _leiste_seite())
        try:
            page.keyboard.press("Tab")
            ring = page.evaluate(
                "() => { const e = document.activeElement;"
                " const s = getComputedStyle(e);"
                " return [e.className, s.outlineStyle, s.outlineWidth,"
                " s.outlineColor, s.outlineOffset]; }"
            )
        finally:
            ctx.close()
        assert ring[0] == "mn-zeitraum-leiste__option"
        assert ring[1:4] == ["solid", "2px", _rgb("web.color.focus-ring")]
        assert ring[4] == "-2px"  # nach innen: overflow:hidden schnitte ihn sonst ab

    def test_navigiert_ohne_skript(self, browser, tmp_path):
        """Die Leiste besteht aus Links: mit abgeschaltetem JavaScript wechselt ein
        Klick die Adresse."""
        datei = tmp_path / "seite.html"
        datei.write_text(_leiste_seite(), encoding="utf-8")
        ctx = browser.new_context(java_script_enabled=False)
        try:
            page = ctx.new_page()
            page.goto(datei.as_uri())
            page.click(f"{_OPTION} >> nth=2")
            assert page.url.endswith("seite.html?tage=2")
        finally:
            ctx.close()


class TestKpiLabelSchmal:
    """mkn-desk Sport-Seite, 390 px (cld1-S117): „TRAININGSBELASTUN / G (TRIMP)“ brach mitten im
    Wort. Das Label trennt jetzt nach Silben (`hyphens: auto`, Seite `lang="de"`) und laeuft
    nie aus der Karte."""

    def test_label_trennt_nach_silben_und_bleibt_in_der_karte(self, browser, tmp_path):
        html = (
            '<div style="width:170px">'
            + render_kpi_card_html(
                KpiCardInput(label="Trainingsbelastung (TRIMP)", value="118 TRIMP")
            )
            + "</div>"
        )
        ctx, page = _geladen(
            browser, tmp_path, _seite(html, render_kpi_card_css()), breite=390
        )
        try:
            hyphens = page.evaluate(
                "getComputedStyle(document.querySelector('.mn-kpi-card__label')).hyphens"
            )
            ueberlauf = page.evaluate(
                "(() => { const e = document.querySelector('.mn-kpi-card__label');"
                " return e.scrollWidth - e.clientWidth; })()"
            )
        finally:
            ctx.close()
        assert hyphens == "auto"
        assert ueberlauf <= 0, f"Label laeuft {ueberlauf}px aus der Karte"


class TestTierChipFallback:
    """Ohne Token-CSS griff fuer JEDEN Tier der gruene Fallback (Bibliothek). Der Fallback ist
    jetzt der Token-Wert des eigenen Tiers."""

    @pytest.mark.parametrize(
        "tier", ["atelier", "kabinett", "observatorium", "magazin"]
    )
    def test_fallback_ohne_tokens_ist_die_eigene_tierfarbe(
        self, browser, tmp_path, tier
    ):
        from mn_design_system.components._patterns.contracts import (
            TierChipInput,
            WebTier,
        )
        from mn_design_system.components.web.tier_chip import (
            render_tier_chip_css,
            render_tier_chip_html,
        )

        chip = render_tier_chip_html(TierChipInput(tier=WebTier(tier), label=tier))
        seite = (
            '<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f"<style>{render_tier_chip_css()}</style></head><body>{chip}</body></html>"
        )
        ctx, page = _geladen(browser, tmp_path, seite)
        try:
            bg = page.evaluate(
                "getComputedStyle(document.querySelector('.mn-tier-chip')).backgroundColor"
            )
        finally:
            ctx.close()
        assert bg == _rgb(f"color.tier.{tier}.bg"), (tier, bg)
