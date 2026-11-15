"""Web-Renderer KPI-Card — HTML + CSS, Welle E.0 (S238).

Konsumiert KpiCardInput aus `_patterns.contracts`. Liefert ein HTML-Snippet
plus optional embedbares CSS.

CSS-Strategie:
- Alle Masse, Schriftgroessen und Linien kommen aus Web-Foundation-Tokens
  (var(--web-*) / var(--space-*)) — `dist/css/tokens.css` muss der Konsument
  in `<head>` einbinden.
- Komponenten-Layout liefert `render_kpi_card_css()`. Konsument kann das
  einmal cachen.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
    KpiWertung,
    SparklineInput,
)
from mn_design_system.components.web.sparkline import render_sparkline_svg
from mn_design_system.tokens import get

_TREND_GLYPH = {
    KpiTrendDirection.UP: "▲",
    KpiTrendDirection.DOWN: "▼",
    KpiTrendDirection.NEUTRAL: "■",
}

_TREND_CLASS = {
    KpiTrendDirection.UP: "is-up",
    KpiTrendDirection.DOWN: "is-down",
    KpiTrendDirection.NEUTRAL: "is-neutral",
}

# Wertungs-Klassen (0.18.0): nur wenn die Polaritaet nicht der Default ist. Die Klasse
# der Bewegung (is-up/is-down/is-neutral) bleibt, die Wertung faerbt sie um — so bleibt
# das HTML eines alten Aufrufs bytegleich.
_WERTUNG_CLASS = {
    KpiWertung.GUT: "is-gut",
    KpiWertung.SCHLECHT: "is-schlecht",
    KpiWertung.NEUTRAL: "is-ungewertet",
}


def render_kpi_card_html(input: KpiCardInput, *, inline_css: bool = False) -> str:
    """KPI-Card als HTML-Snippet.

    inline_css=True hangt das Komponenten-CSS innerhalb eines <style>-Blocks
    direkt an — fuer Single-Snippet-Embeds (z.B. E-Mail-Newsletter).
    """
    direction = input.trend_direction()
    trend_class = _TREND_CLASS[direction]
    trend_glyph = _TREND_GLYPH[direction]

    label = escape(input.label)
    value = escape(input.value)

    parts = []
    if inline_css:
        parts.append(f"<style>{render_kpi_card_css()}</style>")

    if input.status == "neutral":
        parts.append('<article class="mn-kpi-card">')
    else:
        parts.append(f'<article class="mn-kpi-card mn-kpi-card--{input.status}">')
    parts.append(f'<div class="mn-kpi-card__label">{label}</div>')
    parts.append(f'<div class="mn-kpi-card__value">{value}</div>')

    delta = input.delta_text()
    if delta is not None or input.change_pct is not None:
        if delta is not None:
            change_str = escape(delta)
        else:
            sign = "+" if input.change_pct > 0 else ""
            change_str = escape(f"{sign}{input.change_pct:.2f}%")
        classes = trend_class
        if input.richtung != "hoeher" and direction != KpiTrendDirection.NEUTRAL:
            classes += f" {_WERTUNG_CLASS[input.wertung()]}"
        parts.append(
            f'<div class="mn-kpi-card__change {classes}">{trend_glyph} {change_str}</div>'
        )

    if input.sparkline_values:
        sparkline_input = SparklineInput(
            values=list(input.sparkline_values),
            width=120.0,
            height=24.0,
        )
        parts.append(
            f'<div class="mn-kpi-card__sparkline">{render_sparkline_svg(sparkline_input)}</div>'
        )

    if input.caption:
        caption = escape(input.caption)
        parts.append(f'<div class="mn-kpi-card__caption">{caption}</div>')

    parts.append("</article>")
    return "".join(parts)


def render_kpi_card_css(*, status: bool = False) -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` in seinen Build-Output einbinden,
    damit `var(--color-light-text)` etc. greift.

    0.18.0: `is-gut` / `is-schlecht` / `is-ungewertet` stehen NACH `is-up` / `is-down` /
    `is-neutral` und haben dieselbe Spezifitaet — die spaetere Regel gewinnt. So wird
    bei `richtung="niedriger"` aus einem Rueckgang (`is-down`) ein gruenes Delta.

    0.25.0: ``status=True`` haengt die Regeln der Statusflaeche an (`_status_css`); ohne das
    Argument ist die Ausgabe byte-gleich zu 0.24.0.
    """
    basis = _BASIS_CSS
    return f"{basis}\n{_status_css()}" if status else basis


_BASIS_CSS = """
.mn-kpi-card {
  display: grid;
  gap: var(--space-1, 4px);
  padding: var(--space-3, 12px) var(--space-4, 16px);
  background: var(--color-light-surface, #ffffff);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-card, 4px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-kpi-card__label {
  font-size: var(--web-text-caption, 12px);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-light-text-muted, #6b7280);
  /* Deutsche Komposita in schmalen Karten: nach Silben trennen (Seite traegt lang="de"),
     als letzte Stufe umbrechen statt aus der Karte laufen. */
  -webkit-hyphens: auto;
  hyphens: auto;
  overflow-wrap: break-word;
}
.mn-kpi-card__value {
  font-size: var(--web-text-h3, 23px);
  line-height: var(--web-leading-h3, 1.3);
  font-weight: 700;
  color: var(--color-light-h1, #312e81);
}
.mn-kpi-card__change {
  font-size: var(--web-text-caption, 12px);
  font-weight: 600;
}
.mn-kpi-card__change.is-up {
  color: var(--color-status-success, #2e7d32);
}
.mn-kpi-card__change.is-down {
  color: var(--color-status-error, #d32f2f);
}
.mn-kpi-card__change.is-neutral {
  color: var(--color-light-text-muted, #6b7280);
}
.mn-kpi-card__change.is-gut {
  color: var(--color-status-success, #2e7d32);
}
.mn-kpi-card__change.is-schlecht {
  color: var(--color-status-error, #d32f2f);
}
.mn-kpi-card__change.is-ungewertet {
  color: var(--color-light-text-muted, #6b7280);
}
.mn-kpi-card__sparkline {
  margin: var(--space-1, 4px) 0;
  line-height: 0;
}
.mn-kpi-card__caption {
  font-size: var(--web-text-caption, 12px);
  font-style: italic;
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()

#: Stufe der Karte -> Token-Stamm der Statusflaeche.
_STATUS_TOKEN = {"ok": "success", "warn": "warning", "bad": "error"}

#: Delta-Klassen in der Reihenfolge des Basis-CSS: die Wertung steht NACH der Bewegung und
#: gewinnt bei gleicher Spezifitaet — die Statusregeln halten dieselbe Reihenfolge ein.
_DELTA_FARBE = (
    ("is-up", "success"),
    ("is-down", "error"),
    ("is-neutral", None),
    ("is-gut", "success"),
    ("is-schlecht", "error"),
    ("is-ungewertet", None),
)

#: Die zwei Wurzeln des Dunkelmodus — derselbe Vertrag wie das Schema-Skript (0.24.0) und der
#: Dunkelblock von mkn-desk: gewaehlt dunkel, oder Systemeinstellung dunkel ohne Wahl hell.
_DUNKEL_GEWAEHLT = ':root[data-schema="dunkel"]'
_DUNKEL_AUTOMATISCH = ':root:not([data-schema="hell"])'


def _v(name: str, token: str) -> str:
    return f"var(--{name}, {get(token)})"


def _status_css() -> str:
    """Statusflaeche der Karte (0.25.0, KT-1 2026-11-15, Optik wie mkn-desk #1972).

    Hell: Toenung als ``background-image`` UEBER der eigenen Flaeche, Rand links
    ``web.stroke.status-edge``; Label, Caption und Delta in den *-on-surface-Toenen (die rohen
    Toene laegen auf der Toenung unter 4,5:1). Dunkel: keine Toenung (die graue Karte bleibt),
    Rand ``web.stroke.line-strong`` und nur der Wert in ``color.dark.status-*``; Label, Caption und
    Delta zurueck auf die Basis-Variablen (der Konsument belegt sie im Dunkeln um).
    """
    alle = ", ".join(f".mn-kpi-card--{s}" for s in _STATUS_TOKEN)
    gedaempft_hell = _v(
        "color-status-text-muted-on-surface", "color.status.text-muted-on-surface"
    )
    regeln: list[str] = []
    for stufe, tok in _STATUS_TOKEN.items():
        flaeche = _v(f"color-status-{tok}-surface", f"color.status.{tok}-surface")
        rand = _v(f"color-status-{tok}-edge", f"color.status.{tok}-edge")
        regeln.append(
            f".mn-kpi-card--{stufe} {{\n"
            f"  background-image: linear-gradient({flaeche}, {flaeche});\n"
            f"  border-left: var(--web-stroke-status-edge, 4px) solid {rand};\n}}"
        )
    regeln.append(
        f":is({alle}) .mn-kpi-card__label, :is({alle}) .mn-kpi-card__caption {{\n"
        f"  color: {gedaempft_hell};\n}}"
    )
    for klasse, tok in _DELTA_FARBE:
        farbe = (
            _v(f"color-status-{tok}-on-surface", f"color.status.{tok}-on-surface")
            if tok
            else gedaempft_hell
        )
        regeln.append(
            f":is({alle}) .mn-kpi-card__change.{klasse} {{\n  color: {farbe};\n}}"
        )

    def dunkel(wurzel: str) -> list[str]:
        r: list[str] = []
        for stufe, tok in _STATUS_TOKEN.items():
            schrift = _v(f"color-dark-status-{tok}", f"color.dark.status-{tok}")
            r.append(
                f"{wurzel} .mn-kpi-card--{stufe} {{\n"
                f"  background-image: none;\n"
                f"  border-left: var(--web-stroke-line-strong, 2px) solid {schrift};\n}}"
            )
            r.append(
                f"{wurzel} .mn-kpi-card--{stufe} .mn-kpi-card__value {{\n"
                f"  color: {schrift};\n}}"
            )
        basis_gedaempft = "var(--color-light-text-muted, #6b7280)"
        r.append(
            f"{wurzel} :is({alle}) .mn-kpi-card__label, "
            f"{wurzel} :is({alle}) .mn-kpi-card__caption {{\n"
            f"  color: {basis_gedaempft};\n}}"
        )
        basis = {
            "success": "var(--color-status-success, #2e7d32)",
            "error": "var(--color-status-error, #d32f2f)",
            None: basis_gedaempft,
        }
        for klasse, tok in _DELTA_FARBE:
            r.append(
                f"{wurzel} :is({alle}) .mn-kpi-card__change.{klasse} {{\n"
                f"  color: {basis[tok]};\n}}"
            )
        return r

    regeln += dunkel(_DUNKEL_GEWAEHLT)
    innen = "\n".join(dunkel(_DUNKEL_AUTOMATISCH))
    regeln.append(f"@media (prefers-color-scheme: dark) {{\n{innen}\n}}")
    return "\n".join(regeln)
