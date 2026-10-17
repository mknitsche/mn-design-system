"""Verlauf-Chart im echten Browser (0.17.0): Wirkung statt Schreibweise.

``test_verlauf_chart.py`` beweist, was die Komponente ERZEUGT. Hier laeuft die
vendorte Apache-ECharts-Datei (common-Build) mit Theme, Loader und einer Option aus
``verlauf_chart_option`` in Chromium — unter einer so strengen CSP wie beim Konsumenten
(``script-src 'self'; style-src 'self'``, kein Inline-Skript, kein Inline-Stil).

Das beantwortet die Frage, die kein Textvergleich beantwortet: enthaelt der
``common``-Build wirklich alles, was die Option benutzt (Linie, Zeitachse, Tooltip,
Legende, dataZoom inside + slider, markArea, markLine, graphic, aria)? ECharts meldet
einen fehlenden Baustein im Minify-Build NICHT (die Warnungen sind herausgeschnitten) —
darum prueft jeder Test eine sichtbare Wirkung (Pixel, Zoom-Zustand, Attribut), nicht
das Ausbleiben einer Meldung.

Nur mit Playwright + Chromium; sonst sichtbar uebersprungen (UNGEPRUEFT), nie still gruen.
"""

from __future__ import annotations

import http.server
import json
import math
import re
import shutil
import threading
from datetime import date, timedelta
from pathlib import Path

import pytest

import mn_design_system
from mn_design_system.components._patterns.contracts import (
    VerlaufChartInput,
    VerlaufMarkierung,
    VerlaufPunkt,
    VerlaufReihe,
)
from mn_design_system.components.web import (
    ECHARTS_DATEI,
    render_font_face,
    render_foundation_css,
    render_verlauf_chart_css,
    render_verlauf_chart_html,
    render_verlauf_chart_js,
    vendor_js_dir,
    web_font_dir,
)
from mn_design_system.components.web.verlauf_chart import verlauf_chart_option
from mn_design_system.tokens import get

_REPO = Path(mn_design_system.__file__).parents[1]

#: So streng wie die Seitenhuelle des Konsumenten: nichts Inline, nichts Fremdes.
_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self'; "
    "img-src 'self' data:; connect-src 'self'"
)


def _rgb(token: str) -> tuple[int, int, int]:
    h = get(token)
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


# ---------------------------------------------------------------------------
# Seite mit vier Diagrammen: Gewicht (alles), Puls (schlicht), zwei leere
# ---------------------------------------------------------------------------


def _tage(n: int, start: date = date(2026, 7, 19)) -> list[date]:
    return [start + timedelta(days=i) for i in range(n)]


def _diagramme() -> dict[str, VerlaufChartInput]:
    tage = _tage(91)
    gewicht = [
        VerlaufPunkt(t=d, wert=round(82.4 - i * 0.04 + 0.5 * math.sin(i / 3), 1))
        for i, d in enumerate(tage)
        if i % 2 == 0
    ]
    gleitend = [
        VerlaufPunkt(t=d, wert=round(82.4 - i * 0.04, 1)) for i, d in enumerate(tage)
    ][14:]
    puls = [
        VerlaufPunkt(t=d, wert=54 + 3 * math.sin(i / 5) + (i % 4))
        for i, d in enumerate(tage)
    ]
    fenster = {"von": date(2026, 7, 19), "bis": date(2026, 10, 17)}
    return {
        "gewicht": VerlaufChartInput(
            titel="Gewicht",
            einheit="kg",
            reihen=[
                VerlaufReihe(label="Waage", punkte=gewicht),
                VerlaufReihe(label="7-Tage-Mittel", punkte=gleitend, art="gleitend"),
            ],
            zielband_min=78.0,
            zielband_max=81.0,
            markierungen=[VerlaufMarkierung(t=date(2026, 9, 20), label="Marathon")],
            dezimalstellen=1,
            **fenster,
        ),
        "puls": VerlaufChartInput(
            titel="Ruhepuls",
            einheit="bpm",
            reihen=[VerlaufReihe(label="Uhr", punkte=puls)],
            dezimalstellen=0,
            hoehe=220,
            **fenster,
        ),
        "leer": VerlaufChartInput(
            titel="HRV",
            einheit="ms",
            reihen=[VerlaufReihe(label="Runalyze", punkte=[])],
            dezimalstellen=0,
            **fenster,
        ),
    }


def _ohne_graphic(html: str) -> str:
    """Dieselbe Figur, aber der Datenblock ohne `graphic` (Differenz-Gegenprobe)."""
    m = re.search(
        r'(<script type="application/json" id="[a-z0-9-]+-daten">)(.*?)</script>', html
    )
    option = json.loads(m.group(2))
    option.pop("graphic", None)
    block = json.dumps(option, ensure_ascii=False).replace("<", "\\u003c")
    return html.replace(m.group(0), f"{m.group(1)}{block}</script>")


def _seite(mit_bibliothek: bool) -> str:
    d = _diagramme()
    figuren = {k: render_verlauf_chart_html(v, kennung=k) for k, v in d.items()}
    figuren["leer-ohne-text"] = (
        _ohne_graphic(figuren["leer"])
        .replace('data-verlauf-chart="leer"', 'data-verlauf-chart="leer-ohne-text"')
        .replace('id="leer-daten"', 'id="leer-ohne-text-daten"')
    )
    koerper = "".join(f'<section class="k">{f}</section>' for f in figuren.values())
    bib = '<script src="/echarts.js" defer></script>' if mit_bibliothek else ""
    return (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<link rel="stylesheet" href="/tokens.css">'
        '<link rel="stylesheet" href="/komponenten.css">'
        f'{bib}<script src="/mn-verlauf-chart.js" defer></script>'
        f"</head><body>{koerper}</body></html>"
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


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    site = tmp_path_factory.mktemp("verlauf-seite")
    shutil.copytree(web_font_dir(), site / "fonts")
    shutil.copy(vendor_js_dir() / ECHARTS_DATEI, site / "echarts.js")
    shutil.copy(_REPO / "dist" / "css" / "tokens.css", site / "tokens.css")
    (site / "mn-verlauf-chart.js").write_text(
        render_verlauf_chart_js(), encoding="utf-8"
    )
    (site / "komponenten.css").write_text(
        render_font_face("/fonts/")
        + "\n"
        + render_foundation_css()
        + "\n"
        + render_verlauf_chart_css()
        + "\nbody{margin:0;padding:16px;font-family:var(--web-font-sans),system-ui}"
        + "\n.k{max-width:760px;margin:0 auto 24px}",
        encoding="utf-8",
    )
    (site / "seite.html").write_text(_seite(True), encoding="utf-8")
    (site / "ohne-bibliothek.html").write_text(_seite(False), encoding="utf-8")
    (site / "dunkel.html").write_text(
        _seite(True).replace(
            '<html lang="de">', '<html lang="de" data-schema="dunkel">'
        ),
        encoding="utf-8",
    )

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(site), **kwargs)

        def end_headers(self):
            self.send_header("Content-Security-Policy", _CSP)
            super().end_headers()

        def log_message(self, *args):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


class _Seite:
    """Eine geladene Seite samt gesammelter Konsole und CSP-Verstoessen."""

    def __init__(self, page, url: str):
        self.page = page
        self.konsole: list[tuple[str, str]] = []
        page.on("console", lambda m: self.konsole.append((m.type, m.text)))
        page.on("pageerror", lambda e: self.konsole.append(("pageerror", str(e))))
        page.add_init_script(
            "window.__csp = [];"
            "document.addEventListener('securitypolicyviolation',"
            " e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));"
        )
        page.goto(url)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)

    def mitte(self, kennung: str, ax: float, ay: float) -> tuple[float, float]:
        """Punkt innerhalb der Flaeche (Anteile ax, ay) in Viewport-Koordinaten — die
        Flaeche wird vorher ins Bild geholt, sonst laeuft die Maus ins Leere."""
        x, y = self.page.evaluate(
            """([k, ax, ay]) => {
              const f = document.querySelector(
                `[data-verlauf-chart="${k}"] .verlauf-chart__flaeche`);
              f.scrollIntoView({block: 'center'});
              const r = f.getBoundingClientRect();
              return [r.x + r.width * ax, r.y + r.height * ay];
            }""",
            [kennung, ax, ay],
        )
        return x, y

    def csp_verstoesse(self) -> list[str]:
        return self.page.evaluate("window.__csp")

    def js(self, ausdruck: str, arg=None):
        return self.page.evaluate(ausdruck, arg)

    def pixel(self, kennung: str, farbe=None, region=None, toleranz: int = 6) -> int:
        """Zaehlt gezeichnete Pixel einer Figur; `farbe` = (r, g, b) +- `toleranz`,
        ohne Farbe: alles mit Deckkraft. `region` = (x0, y0, x1, y1) in CSS-Pixeln."""
        return self.page.evaluate(
            """([kennung, farbe, region, tol]) => {
              const el = document.querySelector(
                `[data-verlauf-chart="${kennung}"] .verlauf-chart__flaeche canvas`);
              const w = el.width, h = el.height;
              const r = region || [0, 0, w, h];
              const d = el.getContext('2d').getImageData(0, 0, w, h).data;
              let n = 0;
              for (let y = Math.max(0, r[1]); y < Math.min(h, r[3]); y++) {
                for (let x = Math.max(0, r[0]); x < Math.min(w, r[2]); x++) {
                  const i = (y * w + x) * 4;
                  if (d[i + 3] < 200 && farbe) continue;
                  if (!farbe) { if (d[i + 3] > 0) n++; continue; }
                  if (Math.abs(d[i] - farbe[0]) <= tol &&
                      Math.abs(d[i + 1] - farbe[1]) <= tol &&
                      Math.abs(d[i + 2] - farbe[2]) <= tol) n++;
                }
              }
              return n;
            }""",
            [
                kennung,
                list(farbe) if farbe else None,
                list(region) if region else None,
                toleranz,
            ],
        )

    def chart_js(self, kennung: str, rumpf: str, arg=None):
        """Fuehrt `rumpf(chart, flaeche, arg)` mit der ECharts-Instanz der Figur aus."""
        return self.page.evaluate(
            f"""([kennung, arg]) => {{
              const flaeche = document.querySelector(
                `[data-verlauf-chart="${{kennung}}"] .verlauf-chart__flaeche`);
              const chart = window.echarts.getInstanceByDom(flaeche);
              return ({rumpf})(chart, flaeche, arg);
            }}""",
            [kennung, arg],
        )


@pytest.fixture(scope="module")
def seite(browser, server):
    ctx = browser.new_context(
        viewport={"width": 1000, "height": 1400},
        device_scale_factor=1,
        reduced_motion="reduce",  # keine Animation: Pixel sind sofort fertig
    )
    s = _Seite(ctx.new_page(), f"{server}/seite.html")
    yield s
    ctx.close()


# ---------------------------------------------------------------------------
# Grundlage: laeuft unter strenger CSP, zeichnet, ohne Konsolenmeldung
# ---------------------------------------------------------------------------


class TestGrundlage:
    def test_keine_konsolenmeldung_und_kein_csp_verstoss(self, seite):
        assert seite.konsole == []
        assert seite.csp_verstoesse() == []

    def test_jede_figur_hat_eine_gezeichnete_canvas(self, seite):
        for kennung in ("gewicht", "puls", "leer"):
            groesse = seite.js(
                """(k) => {
                  const c = document.querySelector(
                    `[data-verlauf-chart="${k}"] canvas`);
                  return [c.width, c.height];
                }""",
                kennung,
            )
            assert groesse[0] > 300 and groesse[1] > 150, (kennung, groesse)
            assert seite.pixel(kennung) > 500, kennung  # nicht leer

    def test_waagerechtes_ziehen_gehoert_dem_diagramm_senkrechtes_der_seite(
        self, seite
    ):
        assert (
            seite.js(
                "getComputedStyle(document.querySelector("
                "'[data-verlauf-chart=puls] .verlauf-chart__flaeche')).touchAction"
            )
            == "pan-y"
        )

    def test_flaeche_hat_die_stufenhoehe(self, seite):
        assert (
            seite.js(
                "document.querySelector('[data-verlauf-chart=puls] .verlauf-chart__flaeche')"
                ".getBoundingClientRect().height"
            )
            == 220
        )

    def test_ohne_bibliothek_bleibt_die_seite_still(self, browser, server):
        ctx = browser.new_context(viewport={"width": 800, "height": 900})
        try:
            s = _Seite(ctx.new_page(), f"{server}/ohne-bibliothek.html")
            assert s.konsole == []
            assert s.js("document.querySelectorAll('canvas').length") == 0
        finally:
            ctx.close()


# ---------------------------------------------------------------------------
# Bausteine des common-Builds: jeder mit sichtbarer Wirkung
# ---------------------------------------------------------------------------


class TestBausteine:
    def test_linie_in_der_theme_farbe(self, seite):
        assert seite.pixel("puls", _rgb("color.diagram.indigo.base")) > 200

    def test_gleitende_reihe_zweite_theme_farbe(self, seite):
        assert seite.pixel("gewicht", _rgb("color.diagram.teal.base")) > 100

    def test_mark_area_zielband(self, seite):
        zielband = _rgb("color.status.success-bg")
        assert seite.pixel("gewicht", zielband, toleranz=0) > 5000
        assert seite.pixel("puls", zielband, toleranz=0) == 0  # Gegenprobe: kein Band

    def test_mark_line_senkrechte_marke(self, seite):
        """An der x-Position der Marke steht eine (gestrichelte) Linie, eine Woche
        daneben nicht."""

        def spalte(datum: str) -> int:
            x = seite.chart_js(
                "gewicht",
                "(c, f, d) => c.convertToPixel({xAxisIndex: 0}, d)",
                datum,
            )
            # Theme-Farbe der Marke (gedaempfter Text), im Plotbereich (Zeilen 36..200)
            return seite.pixel(
                "gewicht",
                _rgb("color.light.text-muted"),
                region=(round(x) - 1, 36, round(x) + 2, 200),
                toleranz=40,
            )

        assert spalte("2026-09-20") > 30
        assert spalte("2026-09-28") < 10  # Gegenprobe: eine Woche daneben keine Linie

    def test_legende_nur_bei_mehreren_reihen(self, seite):
        band = (500, 0, 1000, 28)  # rechts oben
        assert seite.pixel("gewicht", region=band) > 100
        assert seite.pixel("puls", region=band) == 0

    def test_zoom_slider_zeichnet_sich(self, seite):
        slider = (0, 230, 1000, 260)  # bottom: 6, height: 18 in einer 260-px-Flaeche
        akzent_weich = _rgb("color.light.accent-soft")
        assert seite.pixel("gewicht", akzent_weich, region=slider, toleranz=2) > 10000
        assert (
            seite.pixel("leer", akzent_weich, toleranz=2) == 0
        )  # ohne Daten kein Slider

    def test_zoom_inside_mit_strg_und_mausrad(self, browser, server):
        """Eigene Seite: das Zoomen veraendert den Zustand und soll keinen anderen
        Test beeinflussen."""
        ctx = browser.new_context(
            viewport={"width": 1000, "height": 1400}, reduced_motion="reduce"
        )
        try:
            s = _Seite(ctx.new_page(), f"{server}/seite.html")
            zoom = lambda: s.chart_js(
                "puls",
                "(c) => { const z = c.getOption().dataZoom[0]; return [z.start, z.end]; }",
            )
            s.page.mouse.move(*s.mitte("puls", 0.5, 0.45))
            s.page.mouse.wheel(0, -400)  # ohne Taste: die Seite scrollt, kein Zoom
            s.page.wait_for_timeout(200)
            assert zoom() == [0, 100]
            s.page.mouse.move(*s.mitte("puls", 0.5, 0.45))
            s.page.keyboard.down("Control")
            s.page.mouse.wheel(0, -400)
            s.page.keyboard.up("Control")
            s.page.wait_for_timeout(300)
            start, ende = zoom()
            assert ende - start < 100, (start, ende)  # herangezoomt
        finally:
            ctx.close()

    def test_graphic_text_im_leeren_fenster(self, seite):
        """Gegenprobe: dieselbe leere Figur OHNE `graphic` hat in der Mitte weniger."""
        mitte = (350, 90, 650, 130)
        mit = seite.pixel("leer", region=mitte)
        ohne = seite.pixel("leer-ohne-text", region=mitte)
        assert mit > ohne + 100, (mit, ohne)

    def test_aria_setzt_das_label_neu(self, seite):
        beschreibung = _diagramme()["gewicht"].beschreibung_text()
        label = seite.chart_js(
            "gewicht",
            """(c, f) => {
              f.removeAttribute('aria-label');
              c.resize();
              return f.getAttribute('aria-label');
            }""",
        )
        assert label == beschreibung

    def test_tooltip_erscheint_beim_ueberfahren(self, seite):
        region = (0, 0, 1000, 260)
        vorher = seite.pixel("puls", region=region)
        x, y = seite.mitte("puls", 0.5, 0.45)
        seite.page.mouse.move(x - 30, y)
        seite.page.mouse.move(x, y)
        seite.page.wait_for_timeout(300)
        assert seite.pixel("puls", region=region) > vorher + 500


# ---------------------------------------------------------------------------
# Loader: deutsche Zahlen und Daten, Groessenanpassung, Theme-Wahl
# ---------------------------------------------------------------------------


class TestLoader:
    def test_achsenbeschriftung_deutsch_ohne_ueberfluessige_nullen(self, seite):
        text = seite.chart_js(
            "gewicht",
            """(c) => {
              const f = c.getOption().yAxis[0].axisLabel.formatter;
              return [f(1234.5), f(80), f(79.25)];
            }""",
        )
        assert text == [
            "1.234,5",
            "80",
            "79,3",
        ]  # dezimalstellen=1, Komma, Tausenderpunkt

    def test_tooltip_text_deutsch(self, seite):
        text = seite.chart_js(
            "gewicht",
            """(c) => c.getOption().tooltip[0].formatter([
              {axisValue: new Date(2026, 9, 10).getTime(), marker: '*',
               seriesName: 'Waage', value: ['2026-10-10', 80.25]},
              {axisValue: new Date(2026, 9, 10).getTime(), marker: '+',
               seriesName: '7-Tage-Mittel', value: ['2026-10-10', 81]}
            ])""",
        )
        assert text == "10.10.2026\n* Waage: 80,3 kg\n+ 7-Tage-Mittel: 81,0 kg"

    def test_tooltip_nennt_die_uhrzeit_bei_zeitpunkten(self, seite):
        text = seite.chart_js(
            "gewicht",
            """(c) => c.getOption().tooltip[0].formatter([
              {axisValue: new Date(2026, 9, 10, 7, 30).getTime(), marker: '',
               seriesName: 'X', value: ['', 1]}
            ])""",
        )
        assert text.splitlines()[0] == "10.10.2026 07:30"

    def test_theme_hell_ist_der_standard_dunkel_nur_bei_gesetztem_schema(
        self, browser, server, seite
    ):
        hell_text = _rgb("color.light.text-muted")
        dunkel_text = _rgb("color.dark.text-muted")
        # Kantenglaettung mischt Farben: ein paar Fremdpixel sind normal, daher
        # "viel" gegen "fast keine" statt Gleichheit mit null.
        assert seite.pixel("puls", hell_text, toleranz=3) > 100
        assert seite.pixel("puls", dunkel_text, toleranz=3) < 20
        ctx = browser.new_context(
            viewport={"width": 1000, "height": 900}, reduced_motion="reduce"
        )
        try:
            d = _Seite(ctx.new_page(), f"{server}/dunkel.html")
            assert d.konsole == []
            assert d.pixel("puls", dunkel_text, toleranz=3) > 100
            assert d.pixel("puls", hell_text, toleranz=3) < 20
        finally:
            ctx.close()

    def test_tooltip_ohne_treffer_ist_leer(self, seite):
        assert (
            seite.chart_js("gewicht", "(c) => c.getOption().tooltip[0].formatter([])")
            == ""
        )

    def test_diagramm_folgt_der_containerbreite(self, browser, server):
        ctx = browser.new_context(
            viewport={"width": 1000, "height": 900}, reduced_motion="reduce"
        )
        try:
            s = _Seite(ctx.new_page(), f"{server}/seite.html")
            breite = lambda: s.js(
                "document.querySelector('[data-verlauf-chart=puls] canvas').getBoundingClientRect().width"
            )
            gross = breite()
            s.page.set_viewport_size({"width": 400, "height": 900})
            s.page.wait_for_timeout(400)
            assert breite() < gross - 200
            flaeche = s.js(
                "document.querySelector('[data-verlauf-chart=puls] .verlauf-chart__flaeche')"
                ".getBoundingClientRect().width"
            )
            assert abs(breite() - flaeche) <= 1
        finally:
            ctx.close()


def test_option_im_browser_ist_die_aus_dem_python(seite):
    """Der Datenblock wird unveraendert gelesen: Reihenzahl und Zielband stimmen."""
    soll = verlauf_chart_option(_diagramme()["gewicht"])
    ist = seite.chart_js(
        "gewicht",
        "(c) => { const o = c.getOption(); return [o.series.length, o.series[0].markArea.data]; }",
    )
    assert ist[0] == len(soll["series"])
    # getOption() ergaenzt Standardwerte (label, emphasis): nur die Grenzen vergleichen
    assert [[ende["yAxis"] for ende in paar] for paar in ist[1]] == [[78, 81]]
