"""Web-Renderer Verlauf-Chart — Zeitreihen-Diagramm auf Apache ECharts (0.17.0).

Konsumiert ``VerlaufChartInput`` aus ``_patterns.contracts``. Die Komponente trennt
vier Dinge, damit jedes einzeln pruefbar bleibt:

- ``verlauf_chart_option(input)``  — die ECharts-Option als REINES JSON: keine Farbe,
  keine Funktion. Farben kommen aus dem Theme, Zahlen- und Datumsformat aus dem Loader.
- ``render_verlauf_chart_html(input, kennung=…)`` — ``<figure>`` mit der Flaeche, der
  Option als Datenblock (``<script type="application/json">``, wird nie ausgefuehrt und
  braucht keinen Nonce) und einer Textlegende.
- ``echarts_theme(schema)`` — das Theme aus den Design-Tokens (hell / dunkel).
- ``render_verlauf_chart_js()`` / ``render_verlauf_chart_css()`` — Loader und Layout, vom
  Konsumenten als EIGENE Dateien ausgeliefert (CSP ``script-src 'self'``, kein
  Inline-Skript, kein ``style=``).

Die Bibliothek selbst liegt vendort unter ``vendor_js_dir()``; der Konsument kopiert sie
unter dem versionierten Namen ``echarts-<ECHARTS_VERSION>.min.js`` in sein
Auslieferverzeichnis und bindet BEIDE Skripte ein (Bibliothek zuerst, dann den Loader).
Fehlt die Bibliothek, beendet sich der Loader ohne Fehler — die Tabelle, die der
Konsument unter das Diagramm legt, bleibt dann die Darstellung.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, time
from html import escape
from typing import Literal

from mn_design_system.components._patterns._verlauf import berlin_wanduhr
from mn_design_system.components._patterns._zahl import zahl_de_kurz
from mn_design_system.components._patterns.contracts import (
    VerlaufChartInput,
    VerlaufReihe,
)
from mn_design_system.components.web.foundation import css_font_stack
from mn_design_system.tokens import get as token_get

_KENNUNG = re.compile(r"[a-z0-9-]+")

#: Darunter zeichnet die Reihe Datenpunkt-Symbole, darueber nur die Linie.
_SYMBOLE_BIS = 60

_HOEHEN_STUFEN: tuple[int, ...] = (180, 220, 260, 320, 400, 600)

_LEERES_FENSTER = "keine Werte im Fenster"

#: Beschriftung der Zeitachse je Stufe (deutsche Schreibweise; ECharts waehlt die
#: Stufe nach der Spanne). `none` ist der Rueckfall fuer ungewoehnliche Stufen.
_ZEIT_FORMAT: dict[str, str] = {
    "year": "{yyyy}",
    "month": "{dd}.{MM}.",
    "day": "{dd}.{MM}.",
    "hour": "{HH}:{mm}",
    "minute": "{HH}:{mm}",
    "second": "{HH}:{mm}:{ss}",
    "millisecond": "{HH}:{mm}:{ss}",
    "none": "{dd}.{MM}.{yyyy}",
}


# ---------------------------------------------------------------------------
# Option
# ---------------------------------------------------------------------------


def _iso(t: datetime) -> str:
    """Berliner Wanduhr als ISO-8601 ohne Zone (ECharts liest sie als Ortszeit); ein
    Tageswert bleibt ein reines Datum."""
    if t.time() == time.min:
        return t.date().isoformat()
    return t.isoformat(timespec="seconds")


def _im_fenster(t: datetime, chart: VerlaufChartInput) -> bool:
    """Ganze Tage, `bis` einschliesslich — auch ein Zeitpunkt am letzten Tag zaehlt."""
    return chart.von <= t.date() <= chart.bis


def _punkte(
    reihe: VerlaufReihe, chart: VerlaufChartInput
) -> list[tuple[datetime, float]]:
    """Punkte im Fenster, nach Berliner Wanduhr aufsteigend."""
    punkte = [(berlin_wanduhr(p.t), p.wert) for p in reihe.punkte]
    return sorted((p for p in punkte if _im_fenster(p[0], chart)), key=lambda p: p[0])


def _reihe_option(
    reihe: VerlaufReihe, punkte: list[tuple[datetime, float]]
) -> dict[str, object]:
    serie: dict[str, object] = {
        "type": "line",
        "name": reihe.label,
        "data": [[_iso(t), wert] for t, wert in punkte],
        "connectNulls": False,
    }
    if reihe.art == "gleitend":
        # Die Glaettung ist Begleitlinie: gestrichelt, ohne Symbole.
        serie["lineStyle"] = {"type": "dashed"}
        serie["symbol"] = "none"
        serie["showSymbol"] = False
    else:
        serie["showSymbol"] = len(punkte) <= _SYMBOLE_BIS
    if reihe.achse == "rechts":
        serie["yAxisIndex"] = 1
    return serie


def _runde_grenzen(tief: float, hoch: float) -> tuple[float, float]:
    """Achsengrenzen mit etwas Luft, auf einen runden Schritt (1, 2, 5 x 10^n) gelegt —
    sonst setzt ECharts an die krumme Untergrenze ein eigenes Label (77,5 neben 78)."""
    spanne = (hoch - tief) or abs(hoch) * 0.1 or 1.0
    roh = spanne / 5
    zehner = 10 ** math.floor(math.log10(roh))
    schritt = next(f * zehner for f in (1, 2, 5, 10) if roh <= f * zehner)
    rand = spanne * 0.1
    unten = math.floor((tief - rand) / schritt) * schritt
    oben = math.ceil((hoch + rand) / schritt) * schritt
    return round(unten, 6), round(oben, 6)


def _werteachse(chart: VerlaufChartInput, alle_werte: list[float]) -> dict[str, object]:
    achse: dict[str, object] = {"type": "value", "scale": True}
    if chart.einheit:
        achse["name"] = chart.einheit
        achse["nameLocation"] = "end"
        achse["nameTextStyle"] = {"align": "left"}
    if chart.zielband_min is not None and chart.zielband_max is not None:
        # markArea erweitert die Achse nicht: ohne feste Grenzen wuerde ein Zielband
        # ausserhalb der Daten abgeschnitten.
        werte = [*alle_werte, chart.zielband_min, chart.zielband_max]
        achse["min"], achse["max"] = _runde_grenzen(min(werte), max(werte))
    return achse


def _rechte_werteachse(chart: VerlaufChartInput) -> dict[str, object]:
    """Zweite Werteachse (0.17.1) fuer Reihen mit ``achse="rechts"``: eigene, freie Skala,
    dieselbe Einheit, kein zweites Gitter (es lege sich schief ueber das erste)."""
    achse: dict[str, object] = {
        "type": "value",
        "scale": True,
        "position": "right",
        "splitLine": {"show": False},
    }
    if chart.einheit:
        achse["name"] = chart.einheit
        achse["nameLocation"] = "end"
        achse["nameTextStyle"] = {"align": "right"}
    return achse


def verlauf_chart_option(chart: VerlaufChartInput) -> dict[str, object]:
    """ECharts-Option fuer das Diagramm — reines JSON, deterministisch, ohne Farben.

    Zeitfenster: ganze Tage von ``von`` bis einschliesslich ``bis``; Punkte ausserhalb
    fehlen. Zeitpunkte erscheinen als Berliner Wanduhr (ein ``date`` bleibt Datum).
    Zahlen- und Datumsformat von Achse und Tooltip setzt der Loader.

    Zweite Werteachse (0.17.1): liegt mindestens eine Reihe auf ``achse="rechts"``, ist
    ``yAxis`` eine Liste aus linker und rechter Achse, und jene Reihen zeigen mit
    ``yAxisIndex: 1`` auf die rechte; sonst bleibt ``yAxis`` ein einzelnes Objekt. Zielband
    und Achsengrenzen gelten nur fuer die linke Achse.
    """
    punkte = [_punkte(r, chart) for r in chart.reihen]
    series = [_reihe_option(r, p) for r, p in zip(chart.reihen, punkte, strict=True)]
    erste = series[0]

    if chart.zielband_min is not None and chart.zielband_max is not None:
        erste["markArea"] = {
            "silent": True,
            "data": [[{"yAxis": chart.zielband_min}, {"yAxis": chart.zielband_max}]],
        }
    marken = [m for m in chart.markierungen if _im_fenster(berlin_wanduhr(m.t), chart)]
    if marken:
        erste["markLine"] = {
            "silent": True,
            "symbol": "none",
            "data": [
                {
                    "xAxis": _iso(berlin_wanduhr(m.t)),
                    "label": {"formatter": m.label, "position": "insideEndTop"},
                }
                for m in marken
            ],
        }

    # Die linke Achse (mit ihrem Zielband) richtet sich nur nach den linken Reihen: eine
    # Summe in anderer Groessenordnung auf der rechten Achse blaeht sie nicht auf.
    links = _werteachse(
        chart,
        [
            w
            for reihe, pkt in zip(chart.reihen, punkte, strict=True)
            if reihe.achse == "links"
            for _, w in pkt
        ],
    )
    hat_rechte_achse = any(r.achse == "rechts" for r in chart.reihen)

    option: dict[str, object] = {
        "animationDuration": 300,
        "aria": {
            "enabled": True,
            "label": {"description": chart.beschreibung_text()},
        },
        "grid": {
            "left": 48,
            "right": 48 if hat_rechte_achse else 12,
            "top": 32,
            "bottom": 56,
        },
        "xAxis": {
            "type": "time",
            "min": chart.von.isoformat(),
            "max": f"{chart.bis.isoformat()}T23:59:59",
            "axisLabel": {"formatter": dict(_ZEIT_FORMAT), "hideOverlap": True},
        },
        "yAxis": [links, _rechte_werteachse(chart)] if hat_rechte_achse else links,
        "series": series,
        "tooltip": {"trigger": "axis", "renderMode": "richText", "confine": True},
    }
    if len(chart.reihen) > 1:
        option["legend"] = {"show": True, "top": 0, "right": 12}
    if any(punkte):
        option["dataZoom"] = [
            {"type": "inside", "zoomOnMouseWheel": "ctrl"},
            {"type": "slider", "height": 18, "bottom": 6},
        ]
    else:
        # Ohne Werte gibt es nichts zu zoomen: nur die Achse und der Hinweis.
        option["graphic"] = {
            "type": "text",
            "left": "center",
            "top": "middle",
            "silent": True,
            "style": {"text": _LEERES_FENSTER, "fontSize": 14},
        }
    return option


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------


def _json_fuer_script(option: dict[str, object]) -> str:
    """JSON fuer einen ``<script type="application/json">``-Block: ``<`` als ``\\u003c``,
    damit weder ``</script`` noch ``<!--`` im Block entstehen koennen."""
    return json.dumps(option, ensure_ascii=False, separators=(",", ":")).replace(
        "<", "\\u003c"
    )


def _legende(chart: VerlaufChartInput) -> str:
    teile = []
    for r in chart.reihen:
        merkmale = []
        if r.art == "gleitend":
            merkmale.append("gestrichelt")
        if r.achse == "rechts":
            merkmale.append("rechte Achse")
        teile.append(f"{r.label} ({', '.join(merkmale)})" if merkmale else r.label)
    text = " · ".join(teile)
    if chart.zielband_min is not None and chart.zielband_max is not None:
        # Ohne ueberfluessige Nullen: „70–74 kg", nicht „70,0–74,0 kg".
        grenzen = (
            f"{zahl_de_kurz(chart.zielband_min, chart.dezimalstellen)}–"
            f"{zahl_de_kurz(chart.zielband_max, chart.dezimalstellen)}"
        )
        einheit = f" {chart.einheit}" if chart.einheit else ""
        text += f". Zielband {grenzen}{einheit}"
    return text


def render_verlauf_chart_html(chart: VerlaufChartInput, *, kennung: str) -> str:
    """``<figure>`` mit Zeichenflaeche, Datenblock und Textlegende.

    kennung: Bezeichner dieses Diagramms auf der Seite (nur ``a-z``, ``0-9``, ``-``);
    er verbindet Figur und Datenblock (``<kennung>-daten``) und muss auf der Seite
    eindeutig sein. Eine andere Schreibweise ist ein ``ValueError`` — der Wert landet
    in Attributen und wird nicht stillschweigend bereinigt.
    """
    if not _KENNUNG.fullmatch(kennung):
        raise ValueError(
            f"kennung darf nur a-z, 0-9 und '-' enthalten (und nicht leer sein), "
            f"nicht {kennung!r}"
        )
    option = verlauf_chart_option(chart)
    return (
        f'<figure class="verlauf-chart" data-verlauf-chart="{kennung}" '
        f'data-dezimalstellen="{chart.dezimalstellen}">'
        f'<div class="verlauf-chart__flaeche verlauf-chart__flaeche--h{chart.hoehe}" '
        f'role="img" aria-label="{escape(chart.beschreibung_text(), quote=True)}">'
        f"</div>"
        f'<script type="application/json" id="{kennung}-daten">'
        f"{_json_fuer_script(option)}</script>"
        f"<figcaption>{escape(_legende(chart))}</figcaption>"
        f"</figure>"
    )


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

#: Reihenfarben in fester Reihenfolge (Token-Familien color.diagram.*).
_REIHEN_FARBEN: tuple[str, ...] = ("indigo", "teal", "amber", "azure")


def echarts_theme(schema: Literal["hell", "dunkel"]) -> dict[str, object]:
    """ECharts-Theme aus den Design-Tokens; jede Farbe ist ein ``token_get``-Wert.

    Text und Gitter liegen auf den Tokens fuer GEDAEMPFTEN Text (``text-muted``, AA
    gegen die Flaeche) statt auf ``color.grey.600`` (#999999, nur 2,8:1) — die Beschriftung
    einer Messreihe muss lesbar bleiben.
    """
    if schema not in ("hell", "dunkel"):
        raise ValueError(f"schema muss 'hell' oder 'dunkel' sein, nicht {schema!r}")
    seite = "light" if schema == "hell" else "dark"
    text = token_get(f"color.{seite}.text-muted")
    tinte = token_get(f"color.{seite}.text")
    flaeche = token_get(
        f"color.{seite}.surface" if schema == "hell" else "color.dark.surface-elev"
    )
    rand = token_get(f"color.{seite}.border")
    gitter = token_get("color.grey.200" if schema == "hell" else "color.dark.border")
    akzent = token_get(f"color.{seite}.accent")
    akzent_weich = token_get(f"color.{seite}.accent-soft")
    groesse = int(token_get("web.text.caption").removesuffix("px"))

    zeitachse = {
        "axisLine": {"lineStyle": {"color": rand}},
        "axisTick": {"lineStyle": {"color": rand}},
        "axisLabel": {"color": text, "fontSize": groesse},
        "splitLine": {"show": False, "lineStyle": {"color": gitter}},
        "axisPointer": {"lineStyle": {"color": rand}},
    }
    werteachse = {
        "axisLine": {"show": False},
        "axisTick": {"show": False},
        "axisLabel": {"color": text, "fontSize": groesse},
        "nameTextStyle": {"color": text, "fontSize": groesse},
        "splitLine": {"show": True, "lineStyle": {"color": gitter}},
    }
    if schema == "hell":
        zielband = {"color": token_get("color.status.success-bg")}
    else:
        # Auf dunklem Grund wuerde das helle success-bg blenden: gleicher Ton wie
        # `color.status.success`, aber mit Deckkraft statt eigener Farbe.
        zielband = {"color": token_get("color.status.success"), "opacity": 0.2}

    return {
        "color": [token_get(f"color.diagram.{n}.base") for n in _REIHEN_FARBEN],
        "backgroundColor": "transparent",
        "textStyle": {
            "color": text,
            "fontFamily": css_font_stack("sans"),
            "fontSize": groesse,
        },
        "line": {
            "smooth": False,
            "symbol": "circle",
            "symbolSize": 6,
            "lineStyle": {"width": 2},
        },
        "timeAxis": zeitachse,
        "valueAxis": werteachse,
        "legend": {"textStyle": {"color": text, "fontSize": groesse}},
        "tooltip": {
            "backgroundColor": flaeche,
            "borderColor": rand,
            "borderWidth": 1,
            "padding": [8, 12],
            "textStyle": {"color": tinte, "fontSize": groesse},
            "axisPointer": {"lineStyle": {"color": rand}},
        },
        "dataZoom": {
            "backgroundColor": "transparent",
            "borderColor": "transparent",
            "fillerColor": akzent_weich,
            "dataBackground": {
                "lineStyle": {"color": rand},
                "areaStyle": {"color": gitter},
            },
            "selectedDataBackground": {
                "lineStyle": {"color": akzent},
                "areaStyle": {"color": akzent_weich},
            },
            "handleStyle": {"color": akzent, "borderColor": akzent},
            "moveHandleStyle": {"color": rand},
            "textStyle": {"color": text, "fontSize": groesse},
        },
        "markArea": {"itemStyle": zielband},
        "markLine": {
            "lineStyle": {"color": text, "type": "dashed", "width": 1},
            "label": {"color": text, "fontSize": groesse},
        },
    }


# ---------------------------------------------------------------------------
# Loader (JS)
# ---------------------------------------------------------------------------

_LOADER = """
"use strict";
(function () {
  if (!window.echarts) return;
  var echarts = window.echarts;
  var THEMES = {};
  THEMES["mn-hell"] = __THEME_HELL__;
  THEMES["mn-dunkel"] = __THEME_DUNKEL__;
  echarts.registerTheme("mn-hell", THEMES["mn-hell"]);
  echarts.registerTheme("mn-dunkel", THEMES["mn-dunkel"]);

  var SPRACHE = "de-DE";

  function zahl(wert, minimum, maximum) {
    return Number(wert).toLocaleString(SPRACHE, {
      minimumFractionDigits: minimum,
      maximumFractionDigits: maximum
    });
  }

  function zeitText(ms) {
    var d = new Date(ms);
    var tag = d.toLocaleDateString(SPRACHE, {
      day: "2-digit", month: "2-digit", year: "numeric"
    });
    if (d.getHours() === 0 && d.getMinutes() === 0) return tag;
    return tag + " " + d.toLocaleTimeString(SPRACHE, {
      hour: "2-digit", minute: "2-digit"
    });
  }

  function tooltipText(params, einheit, dezimalstellen) {
    if (!params.length) return "";
    var zeilen = [zeitText(params[0].axisValue)];
    params.forEach(function (p) {
      zeilen.push(
        p.marker + " " + p.seriesName + ": " +
        zahl(p.value[1], dezimalstellen, dezimalstellen) +
        (einheit ? " " + einheit : "")
      );
    });
    return zeilen.join("\\n");
  }

  function start(figur) {
    var flaeche = figur.querySelector(".verlauf-chart__flaeche");
    var daten = document.getElementById(
      figur.getAttribute("data-verlauf-chart") + "-daten"
    );
    if (!flaeche || !daten) return;
    var option = JSON.parse(daten.textContent);
    var dezimalstellen = parseInt(figur.getAttribute("data-dezimalstellen"), 10);
    var achsen = Array.isArray(option.yAxis) ? option.yAxis : [option.yAxis];
    var einheit = achsen[0].name || "";
    var dunkel = document.documentElement.dataset.schema === 'dunkel';
    var schema = dunkel ? "mn-dunkel" : "mn-hell";

    achsen.forEach(function (achse) {
      achse.axisLabel = {
        formatter: function (wert) { return zahl(wert, 0, dezimalstellen); }
      };
    });
    option.tooltip.formatter = function (params) {
      return tooltipText(params, einheit, dezimalstellen);
    };
    if (option.graphic) {
      option.graphic.style.fill = THEMES[schema].textStyle.color;
      option.graphic.style.fontFamily = THEMES[schema].textStyle.fontFamily;
    }
    if (window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      option.animation = false;
    }

    var chart = echarts.init(flaeche, schema, {renderer: 'canvas'});
    chart.setOption(option);
    if (window.ResizeObserver) {
      new ResizeObserver(function () { chart.resize(); }).observe(flaeche);
    } else {
      window.addEventListener("resize", function () { chart.resize(); });
    }
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { chart.resize(); });
    }
  }

  function alle() {
    Array.prototype.forEach.call(
      document.querySelectorAll("[data-verlauf-chart]"), start
    );
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", alle);
  } else {
    alle();
  }
})();
"""


def render_verlauf_chart_js() -> str:
    """Loader-Skript: registriert beide Themes und startet jedes ``[data-verlauf-chart]``.

    Der Konsument legt den Text als eigene Datei ab (z. B. ``mn-verlauf-chart.js``) und
    bindet sie NACH der Bibliothek ein: ``<script src="…" defer>`` (unter einer
    Nonce-CSP traegt das Tag das Nonce der Antwort). NIE als Inline-Skript.

    Verhalten: liest die Option aus dem Datenblock ``#<kennung>-daten``, setzt das
    deutsche Zahlenformat (``Intl``, aus ``data-dezimalstellen`` und der Einheit der
    Werteachse) in Achse und Tooltip, waehlt das Theme ``mn-dunkel`` nur bei
    ``<html data-schema="dunkel">`` (die Seitenhuelle setzt es heute nicht), zeichnet auf
    Canvas, folgt der Containerbreite per ``ResizeObserver`` und schaltet bei
    ``prefers-reduced-motion`` die Animation ab. Fehlt ``window.echarts``, tut der Loader
    nichts. Kein ``eval``, kein ``innerHTML``, keine URL.
    """
    loader = _LOADER.replace(
        "__THEME_HELL__", json.dumps(echarts_theme("hell"), ensure_ascii=False)
    ).replace(
        "__THEME_DUNKEL__", json.dumps(echarts_theme("dunkel"), ensure_ascii=False)
    )
    return loader.strip() + "\n"


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------


def render_verlauf_chart_css() -> str:
    """Komponenten-CSS — Layout, Hoehenstufen als Klassen, Textlegende.

    Die Hoehe kommt NIE als ``style=``-Attribut, sondern ueber eine Klasse je Stufe
    (``--h180`` … ``--h600``), die eine Custom Property setzt. ``touch-action: pan-y``
    laesst die Seite senkrecht scrollen, waehrend waagerechtes Ziehen und Pinch beim
    Diagramm ankommen.
    """
    stufen = "\n".join(
        f".verlauf-chart__flaeche--h{h} {{\n  --verlauf-hoehe: {h}px;\n}}"
        for h in _HOEHEN_STUFEN
    )
    return (
        """
.verlauf-chart {
  margin: 0;
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.verlauf-chart__flaeche {
  width: 100%;
  height: var(--verlauf-hoehe, 260px);
  touch-action: pan-y;
}
.verlauf-chart figcaption {
  margin-top: var(--space-2, 8px);
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
        + "\n"
        + stufen
    )
