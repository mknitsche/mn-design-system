"""Verlauf-Chart (0.17.0): Option, HTML, Theme, Loader, CSS.

Die Komponente liefert ein Zeitreihen-Diagramm auf Apache ECharts. Die Aufteilung ist
bewusst streng:

- ``verlauf_chart_option`` ist reines JSON ohne Farben und ohne Funktionen — Farben
  kommen aus dem Theme (Tokens), Zahlen-/Datumsformat aus dem Loader.
- ``render_verlauf_chart_html`` legt die Option als Datenblock ab
  (``<script type="application/json">``), nie als ausfuehrbares Skript.
- Kein ``style=``, kein ``src=``, kein Inline-Skript: die Komponente laeuft unter
  ``script-src 'self'`` / ``style-src 'self'``.

Die Wirkung im Browser (Zeichnen, CSP, Tooltip) beweist ``test_verlauf_chart_browser.py``.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import date, datetime, timezone

import pytest

from mn_design_system.components._patterns.contracts import (
    VerlaufChartInput,
    VerlaufMarkierung,
    VerlaufPunkt,
    VerlaufReihe,
)
from mn_design_system.components.web import verlauf_chart as vc
from mn_design_system.components.web.verlauf_chart import (
    echarts_theme,
    render_verlauf_chart_css,
    render_verlauf_chart_html,
    render_verlauf_chart_js,
    verlauf_chart_option,
)
from mn_design_system.tokens import TOKENS, get

# ---------------------------------------------------------------------------
# Hilfen — erfundene Zahlen, keine echten Werte
# ---------------------------------------------------------------------------


def _p(tag: int, wert: float, monat: int = 10) -> VerlaufPunkt:
    return VerlaufPunkt(t=date(2026, monat, tag), wert=wert)


def _reihe(
    label: str = "Gewicht", *, art: str = "messung", punkte=None
) -> VerlaufReihe:
    if punkte is None:
        punkte = [_p(3, 80.0), _p(9, 79.4), _p(16, 79.0)]
    return VerlaufReihe(label=label, punkte=punkte, art=art)


def _chart(**overrides) -> VerlaufChartInput:
    base = {
        "titel": "Gewicht",
        "einheit": "kg",
        "reihen": [_reihe()],
        "von": date(2026, 10, 1),
        "bis": date(2026, 10, 17),
    }
    base.update(overrides)
    return VerlaufChartInput(**base)


def _hex_alle(node) -> set[str]:
    """Alle `#rrggbb`-Zeichenketten irgendwo in einer verschachtelten Struktur."""
    return set(re.findall(r"#[0-9a-fA-F]{3,8}\b", json.dumps(node)))


def _daten_block(html: str) -> str:
    m = re.search(
        r'<script type="application/json" id="[a-z0-9-]+-daten">(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert m, html
    return m.group(1)


# ---------------------------------------------------------------------------
# Option
# ---------------------------------------------------------------------------


class TestOption:
    def test_eine_reihe_je_eingabe_reihe(self):
        c = _chart(reihen=[_reihe("A"), _reihe("B"), _reihe("C")])
        option = verlauf_chart_option(c)
        assert [s["name"] for s in option["series"]] == ["A", "B", "C"]
        assert all(s["type"] == "line" for s in option["series"])

    def test_zeitachse_steht_von_bis_ein_ganzer_tag(self):
        x = verlauf_chart_option(_chart())["xAxis"]
        assert x["type"] == "time"
        assert x["min"] == "2026-10-01"
        # `bis` gilt einschliesslich: ein Wert am Nachmittag von `bis` liegt noch auf der Achse
        assert x["max"] == "2026-10-17T23:59:59"

    def test_werteachse_traegt_die_einheit(self):
        y = verlauf_chart_option(_chart())["yAxis"]
        assert y["type"] == "value"
        assert y["name"] == "kg"

    def test_werteachse_ohne_einheit_hat_keinen_namen(self):
        y = verlauf_chart_option(_chart(einheit=""))["yAxis"]
        assert "name" not in y

    def test_punkte_als_iso_wert_paare_aufsteigend_sortiert(self):
        reihe = _reihe(punkte=[_p(9, 79.4), _p(3, 80.0), _p(16, 79.0)])
        data = verlauf_chart_option(_chart(reihen=[reihe]))["series"][0]["data"]
        assert data == [
            ["2026-10-03", 80.0],
            ["2026-10-09", 79.4],
            ["2026-10-16", 79.0],
        ]

    def test_punkt_ausserhalb_des_fensters_fehlt(self):
        reihe = _reihe(
            punkte=[_p(30, 1.0, monat=9), _p(3, 2.0), _p(17, 3.0), _p(18, 4.0)]
        )
        data = verlauf_chart_option(_chart(reihen=[reihe]))["series"][0]["data"]
        assert [d[0] for d in data] == ["2026-10-03", "2026-10-17"]

    def test_zeitpunkt_am_bis_tag_gehoert_noch_ins_fenster(self):
        """Blutdruck um 07:30 am letzten Tag darf nicht verschwinden."""
        spaet = VerlaufPunkt(t=datetime(2026, 10, 17, 7, 30), wert=120)  # noqa: DTZ001
        data = verlauf_chart_option(_chart(reihen=[_reihe(punkte=[spaet])]))
        assert data["series"][0]["data"] == [["2026-10-17T07:30:00", 120]]

    def test_zeitzone_wird_auf_berliner_wanduhr_umgerechnet(self):
        """Ein UTC-Zeitstempel erscheint als Berliner Uhrzeit (MESZ = UTC+2); ein
        naiver Zeitstempel gilt schon als Berliner Uhrzeit."""
        utc = VerlaufPunkt(t=datetime(2026, 10, 9, 5, 30, tzinfo=timezone.utc), wert=1)
        naiv = VerlaufPunkt(t=datetime(2026, 10, 10, 7, 30), wert=2)  # noqa: DTZ001
        reihe = _reihe(punkte=[naiv, utc])
        data = verlauf_chart_option(_chart(reihen=[reihe]))["series"][0]["data"]
        assert data == [["2026-10-09T07:30:00", 1], ["2026-10-10T07:30:00", 2]]

    def test_datum_und_zeitpunkt_gemischt_werden_sortiert(self):
        mittag = VerlaufPunkt(t=datetime(2026, 10, 9, 12, 0), wert=2)  # noqa: DTZ001
        reihe = _reihe(punkte=[mittag, _p(10, 3.0), _p(9, 1.0)])
        data = verlauf_chart_option(_chart(reihen=[reihe]))["series"][0]["data"]
        assert [d[1] for d in data] == [1.0, 2, 3.0]

    def test_gleitend_ist_gestrichelt_ohne_symbole(self):
        c = _chart(reihen=[_reihe("Messung"), _reihe("7-Tage", art="gleitend")])
        mess, gleit = verlauf_chart_option(c)["series"]
        assert gleit["lineStyle"]["type"] == "dashed"
        assert gleit["symbol"] == "none"
        assert gleit["showSymbol"] is False
        assert mess.get("lineStyle", {}).get("type") != "dashed"

    def test_symbole_nur_bis_60_punkte(self):
        wenig = _reihe(punkte=[_p(1 + i % 17, float(i), monat=10) for i in range(60)])
        viel = _reihe(punkte=[_p(1 + i % 17, float(i), monat=10) for i in range(61)])
        assert verlauf_chart_option(_chart(reihen=[wenig]))["series"][0]["showSymbol"]
        assert not verlauf_chart_option(_chart(reihen=[viel]))["series"][0][
            "showSymbol"
        ]

    def test_zielband_nur_mit_zielband(self):
        ohne = verlauf_chart_option(_chart())["series"][0]
        mit = verlauf_chart_option(_chart(zielband_min=78.0, zielband_max=80.0))
        assert "markArea" not in ohne
        assert mit["series"][0]["markArea"]["data"] == [
            [{"yAxis": 78.0}, {"yAxis": 80.0}]
        ]
        assert all("markArea" not in s for s in mit["series"][1:])

    def test_zielband_liegt_im_sichtbaren_bereich_der_werteachse(self):
        """markArea erweitert die Achse nicht — ein Band ausserhalb der Daten
        wuerde sonst abgeschnitten."""
        y = verlauf_chart_option(_chart(zielband_min=70.0, zielband_max=75.0))["yAxis"]
        assert y["min"] <= 70.0 and y["max"] >= 80.0  # Band UND Daten (79..80)

    def test_werteachse_grenzen_sind_runde_werte(self):
        """Krumme Grenzen (77,5) bekaemen von ECharts ein eigenes, klemmendes Label."""
        daten = _reihe(punkte=[_p(3, 78.3), _p(9, 80.4), _p(16, 82.7)])
        y = verlauf_chart_option(
            _chart(reihen=[daten], zielband_min=78.0, zielband_max=81.0)
        )["yAxis"]
        assert (y["min"], y["max"]) == (77.0, 84.0)

    def test_werteachse_ohne_zielband_hat_keine_festen_grenzen(self):
        y = verlauf_chart_option(_chart())["yAxis"]
        assert "min" not in y and "max" not in y

    def test_werteachse_grenzen_bei_gleichen_werten(self):
        """Kein Teilen durch null, wenn Daten und Band auf einem Wert liegen."""
        reihe = _reihe(punkte=[_p(3, 80.0)])
        y = verlauf_chart_option(
            _chart(reihen=[reihe], zielband_min=80.0, zielband_max=80.0)
        )["yAxis"]
        assert y["min"] < 80.0 < y["max"]

    def test_markierungen_nur_mit_markierungen(self):
        ohne = verlauf_chart_option(_chart())["series"][0]
        assert "markLine" not in ohne
        m = [
            VerlaufMarkierung(t=date(2026, 10, 10), label="Marathon"),
            VerlaufMarkierung(t=date(2026, 9, 1), label="ausserhalb"),
        ]
        mit = verlauf_chart_option(_chart(markierungen=m))["series"][0]["markLine"]
        assert mit["symbol"] == "none"
        assert len(mit["data"]) == 1  # die ausserhalb des Fensters entfaellt
        assert mit["data"][0]["xAxis"] == "2026-10-10"
        assert mit["data"][0]["label"]["formatter"] == "Marathon"

    def test_zoom_inside_und_slider(self):
        zoom = verlauf_chart_option(_chart())["dataZoom"]
        assert [z["type"] for z in zoom] == ["inside", "slider"]

    def test_mausrad_zoomt_nur_mit_taste(self):
        """Ohne Taste wuerde das Mausrad die Seite nicht mehr scrollen, sobald der
        Zeiger ueber dem Diagramm steht."""
        inside = verlauf_chart_option(_chart())["dataZoom"][0]
        assert inside["zoomOnMouseWheel"] in {"ctrl", "shift", "alt"}

    def test_tooltip_axis_richtext_confine(self):
        tip = verlauf_chart_option(_chart())["tooltip"]
        assert tip["trigger"] == "axis"
        assert tip["renderMode"] == "richText"
        assert tip["confine"] is True

    def test_legende_nur_bei_mehreren_reihen(self):
        assert "legend" not in verlauf_chart_option(_chart())
        zwei = verlauf_chart_option(_chart(reihen=[_reihe("A"), _reihe("B")]))
        assert zwei["legend"]["show"] is True

    def test_aria_mit_beschreibung(self):
        aria = verlauf_chart_option(_chart(beschreibung="Eigener Text"))["aria"]
        assert aria == {"enabled": True, "label": {"description": "Eigener Text"}}

    def test_aria_default_aus_den_daten(self):
        aria = verlauf_chart_option(_chart())["aria"]
        assert "Gewicht" in aria["label"]["description"]
        assert "79,0" in aria["label"]["description"]

    def test_animation_kurz(self):
        assert verlauf_chart_option(_chart())["animationDuration"] == 300

    def test_grid_kompakt(self):
        grid = verlauf_chart_option(_chart())["grid"]
        assert grid["left"] == 48 and grid["right"] == 12

    def test_leeres_fenster_zeigt_text_statt_daten(self):
        leer = _chart(reihen=[_reihe(punkte=[])])
        option = verlauf_chart_option(leer)
        assert option["graphic"]["type"] == "text"
        assert option["graphic"]["style"]["text"] == "keine Werte im Fenster"
        assert option["series"][0]["data"] == []
        assert option["xAxis"]["min"] == "2026-10-01"  # die Achse steht trotzdem

    def test_graphic_nur_bei_leerem_fenster(self):
        assert "graphic" not in verlauf_chart_option(_chart())

    def test_leeres_fenster_ohne_zoom(self):
        """Ohne Werte gibt es nichts zu zoomen."""
        leer = _chart(reihen=[_reihe(punkte=[])])
        assert "dataZoom" not in verlauf_chart_option(leer)

    def test_punkte_nur_ausserhalb_des_fensters_gelten_als_leer(self):
        reihe = _reihe(punkte=[_p(5, 1.0, monat=8)])
        assert "graphic" in verlauf_chart_option(_chart(reihen=[reihe]))

    def test_keine_farben_in_der_option(self):
        """Farben kommen ausschliesslich aus dem Theme (Tokens)."""
        c = _chart(
            reihen=[_reihe("A"), _reihe("B", art="gleitend")],
            zielband_min=78.0,
            zielband_max=80.0,
            markierungen=[VerlaufMarkierung(t=date(2026, 10, 10), label="M")],
        )
        text = json.dumps(verlauf_chart_option(c))
        assert "#" not in text
        assert "rgb" not in text.lower()
        assert not re.search(
            r'"(color|fill|stroke|background\w*)"', text, re.IGNORECASE
        )

    def test_reines_json_ohne_funktionen(self):
        c = _chart(zielband_min=78.0, zielband_max=80.0)
        text = json.dumps(verlauf_chart_option(c))
        assert "function" not in text
        assert "=>" not in text

    def test_zwei_aufrufe_liefern_dasselbe(self):
        c = _chart(zielband_min=78.0, zielband_max=80.0)
        assert verlauf_chart_option(c) == verlauf_chart_option(c)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------


class TestHtml:
    def test_aufbau(self):
        html = render_verlauf_chart_html(_chart(), kennung="gewicht")
        assert html.startswith('<figure class="verlauf-chart"')
        assert 'data-verlauf-chart="gewicht"' in html
        assert 'data-dezimalstellen="1"' in html
        assert 'class="verlauf-chart__flaeche verlauf-chart__flaeche--h260"' in html
        assert 'role="img"' in html
        assert '<script type="application/json" id="gewicht-daten">' in html
        assert "<figcaption>" in html and html.endswith("</figure>")

    def test_hoehenstufe_wird_klasse(self):
        html = render_verlauf_chart_html(_chart(hoehe=400), kennung="x")
        assert "verlauf-chart__flaeche--h400" in html

    def test_json_block_ist_parsebar_und_gleich_der_option(self):
        c = _chart(zielband_min=78.0, zielband_max=80.0)
        html = render_verlauf_chart_html(c, kennung="gewicht")
        assert json.loads(_daten_block(html)) == verlauf_chart_option(c)

    def test_json_block_kann_das_script_nicht_schliessen(self):
        c = _chart(reihen=[_reihe("</script><img src=x onerror=alert(1)>")])
        html = render_verlauf_chart_html(c, kennung="gewicht")
        assert html.lower().count("</script") == 1  # nur das eigene Ende
        assert "<img" not in html

    def test_label_mit_spitzen_klammern(self):
        c = _chart(reihen=[_reihe("<b>")])
        html = render_verlauf_chart_html(c, kennung="gewicht")
        block = _daten_block(html)
        assert "<" not in block  # im Block nur als <
        assert "\\u003cb>" in block
        assert json.loads(block)["series"][0]["name"] == "<b>"  # unverfaelscht
        caption = html.split("<figcaption>")[1]
        assert "&lt;b&gt;" in caption and "<b>" not in caption

    def test_kein_style_kein_src_kein_inline_skript(self):
        c = _chart(zielband_min=78.0, zielband_max=80.0)
        html = render_verlauf_chart_html(c, kennung="gewicht")
        assert "style=" not in html
        assert "src=" not in html
        assert len(re.findall(r"<script", html)) == 1  # nur der Datenblock
        assert 'type="application/json"' in html

    def test_aria_label_ist_escaped(self):
        c = _chart(beschreibung='x" onmouseover="alert(1)')
        html = render_verlauf_chart_html(c, kennung="gewicht")
        assert 'aria-label="x&quot; onmouseover=&quot;alert(1)"' in html
        assert 'onmouseover="alert' not in html

    def test_aria_label_default_nennt_letztstand(self):
        html = render_verlauf_chart_html(_chart(), kennung="gewicht")
        assert re.search(r'aria-label="[^"]*79,0 kg[^"]*"', html)

    @pytest.mark.parametrize(
        "kennung", ["", "x y", "X", "a_b", 'a"b', "a<b", "ä", "a/b", "a b"]
    )
    def test_kennung_nur_klein_ziffern_bindestrich(self, kennung):
        with pytest.raises(ValueError, match="kennung"):
            render_verlauf_chart_html(_chart(), kennung=kennung)

    def test_kennung_mit_zeilenumbruch_abgelehnt(self):
        """`$` in einem Regex trifft vor einem Zeilenende — fullmatch darf das nicht."""
        with pytest.raises(ValueError, match="kennung"):
            render_verlauf_chart_html(_chart(), kennung="abc\n")

    def test_caption_nennt_reihen_und_gleitend(self):
        c = _chart(reihen=[_reihe("Waage"), _reihe("7-Tage-Mittel", art="gleitend")])
        caption = render_verlauf_chart_html(c, kennung="g").split("<figcaption>")[1]
        assert "Waage" in caption
        assert "7-Tage-Mittel (gestrichelt)" in caption

    def test_caption_nennt_zielband_mit_einheit(self):
        c = _chart(zielband_min=78.0, zielband_max=80.5)
        caption = render_verlauf_chart_html(c, kennung="g").split("<figcaption>")[1]
        assert "Zielband" in caption
        assert "78,0" in caption and "80,5" in caption and "kg" in caption

    def test_caption_ohne_zielband_kein_zielband_satz(self):
        caption = render_verlauf_chart_html(_chart(), kennung="g").split(
            "<figcaption>"
        )[1]
        assert "Zielband" not in caption

    def test_deterministisch(self):
        c = _chart(zielband_min=78.0, zielband_max=80.0)
        assert render_verlauf_chart_html(c, kennung="g") == render_verlauf_chart_html(
            c, kennung="g"
        )


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------


def _luminanz(hexfarbe: str) -> float:
    r, g, b = (int(hexfarbe[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _kontrast(a: str, b: str) -> float:
    la, lb = sorted((_luminanz(a), _luminanz(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class TestTheme:
    @pytest.mark.parametrize("schema", ["hell", "dunkel"])
    def test_vier_reihenfarben_aus_den_tokens(self, schema):
        farben = echarts_theme(schema)["color"]
        assert farben == [
            get("color.diagram.indigo.base"),
            get("color.diagram.teal.base"),
            get("color.diagram.amber.base"),
            get("color.diagram.azure.base"),
        ]

    @pytest.mark.parametrize("schema", ["hell", "dunkel"])
    def test_jede_hex_farbe_ist_ein_token_wert(self, schema):
        """Keine Farbe im Theme, die nicht aus `token_get` kommt."""
        token_werte = {str(v).lower() for v in TOKENS.values()}
        gefunden = _hex_alle(echarts_theme(schema))
        assert gefunden, "Untergrenze: ein Theme ohne Hex-Farben prueft nichts"
        assert {h.lower() for h in gefunden} <= token_werte

    @pytest.mark.parametrize("schema", ["hell", "dunkel"])
    def test_hintergrund_transparent_und_schrift_aus_dem_token(self, schema):
        theme = echarts_theme(schema)
        assert theme["backgroundColor"] == "transparent"
        assert "Geist" in theme["textStyle"]["fontFamily"]

    def test_hell_und_dunkel_unterscheiden_sich_in_text_und_gitter(self):
        hell, dunkel = echarts_theme("hell"), echarts_theme("dunkel")
        assert hell["textStyle"]["color"] != dunkel["textStyle"]["color"]
        assert hell["timeAxis"]["splitLine"] != dunkel["timeAxis"]["splitLine"]

    def test_zielband_hell_ist_success_bg(self):
        fill = echarts_theme("hell")["markArea"]["itemStyle"]["color"]
        assert fill == get("color.status.success-bg")

    def test_achsenbeschriftung_hat_lesbaren_kontrast(self):
        """WCAG 1.4.3: 4,5:1 fuer kleinen Text — die Beschriftung sitzt auf dem
        Seitenhintergrund (hell: Flaeche, dunkel: dunkle Flaeche)."""
        hell = echarts_theme("hell")["valueAxis"]["axisLabel"]["color"]
        dunkel = echarts_theme("dunkel")["valueAxis"]["axisLabel"]["color"]
        assert _kontrast(hell, get("color.light.surface")) >= 4.5
        assert _kontrast(dunkel, get("color.dark.surface")) >= 4.5

    def test_reihenfarben_haben_grafik_kontrast(self):
        """WCAG 1.4.11: Linien brauchen 3:1 gegen den Untergrund."""
        for farbe in echarts_theme("hell")["color"]:
            assert _kontrast(farbe, get("color.light.surface")) >= 3.0, farbe
        for farbe in echarts_theme("dunkel")["color"]:
            assert _kontrast(farbe, get("color.dark.surface")) >= 3.0, farbe

    def test_unbekanntes_schema_ist_ein_fehler(self):
        with pytest.raises(ValueError, match="schema"):
            echarts_theme("sepia")  # type: ignore[arg-type]

    def test_deterministisch(self):
        assert echarts_theme("hell") == echarts_theme("hell")


# ---------------------------------------------------------------------------
# Loader (JS)
# ---------------------------------------------------------------------------


class TestJs:
    def test_registriert_beide_themes(self):
        js = render_verlauf_chart_js()
        assert 'registerTheme("mn-hell"' in js
        assert 'registerTheme("mn-dunkel"' in js

    def test_eingebettete_themes_sind_die_aus_dem_python(self):
        js = render_verlauf_chart_js()
        for schema in ("hell", "dunkel"):
            assert json.dumps(echarts_theme(schema), ensure_ascii=False) in js

    def test_erste_anweisung_beendet_ohne_echarts(self):
        """Ohne Bibliothek bleibt die Tabelle die Darstellung — kein Fehler."""
        js = render_verlauf_chart_js()
        koerper = js.split("(function () {", 1)[1]
        erste = next(z.strip() for z in koerper.splitlines() if z.strip())
        assert erste == "if (!window.echarts) return;"

    def test_dunkel_nur_bei_gesetztem_schema(self):
        assert "dataset.schema === 'dunkel'" in render_verlauf_chart_js()

    def test_resize_observer_und_canvas(self):
        js = render_verlauf_chart_js()
        assert "ResizeObserver" in js
        assert "renderer: 'canvas'" in js

    def test_reduzierte_bewegung_schaltet_animation_ab(self):
        assert "prefers-reduced-motion" in render_verlauf_chart_js()

    @pytest.mark.parametrize(
        "verboten",
        [
            "eval(",
            "new Function",
            "innerHTML",
            "outerHTML",
            "document.write",
            "http",
            "//cdn",
        ],
    )
    def test_keine_gefaehrlichen_oder_externen_bausteine(self, verboten):
        assert verboten not in render_verlauf_chart_js()

    @pytest.mark.skipif(
        shutil.which("node") is None, reason="node fehlt — Syntax UNGEPRUEFT"
    )
    def test_syntax_gueltig(self, tmp_path):
        datei = tmp_path / "loader.js"
        datei.write_text(render_verlauf_chart_js(), encoding="utf-8")
        ergebnis = subprocess.run(
            ["node", "--check", str(datei)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert ergebnis.returncode == 0, ergebnis.stderr

    def test_deterministisch(self):
        assert render_verlauf_chart_js() == render_verlauf_chart_js()


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------


class TestCss:
    def test_sechs_hoehenklassen(self):
        css = render_verlauf_chart_css()
        for stufe in (180, 220, 260, 320, 400, 600):
            assert f".verlauf-chart__flaeche--h{stufe}" in css
            assert f"{stufe}px" in css

    def test_hoehenstufen_stimmen_mit_dem_vertrag_ueberein(self):
        from typing import get_args

        stufen = get_args(VerlaufChartInput.model_fields["hoehe"].annotation)
        css = render_verlauf_chart_css()
        assert set(stufen) == {180, 220, 260, 320, 400, 600}
        assert all(f"--h{s}" in css for s in stufen)

    def test_flaeche_voll_breit(self):
        css = render_verlauf_chart_css()
        assert re.search(r"\.verlauf-chart__flaeche\s*\{[^}]*width:\s*100%", css)

    def test_keine_hex_farbe_ausser_als_var_fallback(self):
        css = render_verlauf_chart_css()
        ohne_var = re.sub(r"var\([^)]*\)", "", css)
        assert "#" not in ohne_var
        assert "var(--" in css

    def test_vertikales_scrollen_bleibt_der_seite(self):
        """touch-action: pan-y — ein Wisch nach oben/unten scrollt die Seite statt das
        Diagramm festzuhalten; waagerechtes Ziehen und Pinch gehen an das Diagramm."""
        assert "touch-action: pan-y" in render_verlauf_chart_css()

    def test_caption_klein_und_gedaempft(self):
        css = render_verlauf_chart_css()
        assert re.search(
            r"\.verlauf-chart figcaption\s*\{[^}]*var\(--web-text-caption", css
        )
        assert "var(--color-light-text-muted" in css

    def test_keine_pt_einheiten(self):
        assert "pt;" not in render_verlauf_chart_css()

    def test_deterministisch(self):
        assert render_verlauf_chart_css() == render_verlauf_chart_css()


# ---------------------------------------------------------------------------
# Paket-Exporte
# ---------------------------------------------------------------------------


def test_exports_im_web_paket():
    from mn_design_system.components import web

    for name in (
        "verlauf_chart_option",
        "render_verlauf_chart_html",
        "render_verlauf_chart_css",
        "render_verlauf_chart_js",
        "echarts_theme",
    ):
        assert getattr(web, name) is getattr(vc, name)
        assert name in web.__all__
