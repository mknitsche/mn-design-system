"""Web-Renderer Content-Card + Card-Grid — HTML + CSS, UX-Welle v0.2.

Konsumiert ContentCardInput und CardGridInput aus `_patterns.contracts`.

- Content-Card: generische Inhalts-Karte (Titel + Text). Optional verlinkt
  und optional tier-getoent (Akzent-Border aus der color.tier-Familie).
  Bewusst getrennt von kpi_card — die KPI-Card ist KPI-spezifisch
  (Trend/Sparkline), die Content-Card ist generisch.
- Card-Grid: responsives Raster, das Content-Cards einbettet. Die Spaltenzahl
  wird als CSS-Variable `--mn-card-grid-cols` am Wrapper gesetzt (kein Hex,
  keine inline-Grid-Template-Hardcodes).

CSS-Strategie wie kpi_card / wetter_strip: Farb- und Schrift-Token via CSS
Custom Properties, Layout-Werte (Grid, Schriftgroessen in rem) inline.

Verlinkte Card (Affordance): bei gesetztem href wird der Titel zum `<a>` UND
die ganze Card via Stretched-Link-Pattern (`__link::after { inset: 0 }`)
ganzflaechig klickbar — `cursor: pointer` am `<article>` ist damit ehrlich.
Eine Card ohne href behaelt den Default-Cursor.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import (
    CardGridInput,
    ContentCardInput,
    WebTier,
)

_TIERS: tuple[WebTier, ...] = (
    WebTier.BIBLIOTHEK,
    WebTier.ATELIER,
    WebTier.KABINETT,
    WebTier.START,
)

# var()-Fallback je Tier-Border — der ECHTE Tier-Wert aus tokens.py
# (color.tier.<tier>.border), damit eine tier-getoente Card auch ohne
# geladene tokens.css ihre Tier-Akzent-Border behaelt statt Einheits-Grau.
_TIER_BORDER_FALLBACK: dict[WebTier, str] = {
    WebTier.BIBLIOTHEK: "#bbf7d0",
    WebTier.ATELIER: "#fde68a",
    WebTier.KABINETT: "#fecaca",
    WebTier.START: "#bbf7d0",
}


def render_content_card_html(
    input: ContentCardInput, *, inline_css: bool = False
) -> str:
    """Content-Card als HTML-Snippet (<article> mit Titel + Text).

    Bei gesetztem href wird der Titel zum Link und die Card traegt
    `mn-content-card--linked` — via Stretched-Link wird die gesamte
    Card-Flaeche klickbar (CSS-Affordance: cursor pointer).
    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_content_card_css()}</style>")

    classes = ["mn-content-card"]
    if input.tier is not None:
        classes.append(f"mn-content-card--{input.tier.value}")
    if input.href is not None:
        classes.append("mn-content-card--linked")

    parts.append(f'<article class="{" ".join(classes)}">')

    title = escape(input.title)
    if input.href is not None:
        href = escape(input.href, quote=True)
        parts.append(
            f'<h3 class="mn-content-card__title">'
            f'<a class="mn-content-card__link" href="{href}">{title}</a>'
            f"</h3>"
        )
    else:
        parts.append(f'<h3 class="mn-content-card__title">{title}</h3>')

    parts.append(f'<p class="mn-content-card__body">{escape(input.body)}</p>')
    parts.append("</article>")
    return "".join(parts)


def render_content_card_css() -> str:
    """Komponenten-CSS — Layout + 4 Tier-Border-Modifier, Token-Werte via
    CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-tier-bibliothek-border)` etc. greift.
    """
    rules = [
        """
.mn-content-card {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 1rem 1.125rem;
  background: var(--color-light-surface, #ffffff);
  border: 1px solid var(--color-light-border, #cbd5e1);
  border-radius: var(--radius-card, 6px);
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
}
.mn-content-card--linked {
  position: relative;
  cursor: pointer;
}
.mn-content-card__title {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.25;
  margin: 0;
  color: var(--color-light-h1, #312e81);
}
.mn-content-card__link {
  text-decoration: none;
  color: inherit;
}
.mn-content-card__link::after {
  content: "";
  position: absolute;
  inset: 0;
}
.mn-content-card__link:hover {
  text-decoration: underline;
}
.mn-content-card__link:focus-visible {
  outline: 2px solid var(--color-light-accent, #4F46E5);
  outline-offset: 2px;
}
.mn-content-card__body {
  font-size: 0.8125rem;
  line-height: 1.5;
  margin: 0;
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        fallback = _TIER_BORDER_FALLBACK[tier]
        rules.append(
            f".mn-content-card--{t} {{\n"
            f"  border-color: var(--color-tier-{t}-border, {fallback});\n"
            f"}}"
        )
    return "\n".join(rules)


def render_card_grid_html(input: CardGridInput, *, inline_css: bool = False) -> str:
    """Card-Grid als HTML-Snippet (<div> mit eingebetteten Content-Cards).

    Die Spaltenzahl landet als CSS-Variable `--mn-card-grid-cols` am Wrapper.
    inline_css=True hangt Grid- UND Card-CSS in einem <style>-Block an.
    """
    parts = []
    if inline_css:
        parts.append(
            f"<style>{render_card_grid_css()}{render_content_card_css()}</style>"
        )

    parts.append(
        f'<div class="mn-card-grid" style="--mn-card-grid-cols:{input.columns}">'
    )
    for card in input.cards:
        parts.append(render_content_card_html(card))
    parts.append("</div>")
    return "".join(parts)


def render_card_grid_css() -> str:
    """Komponenten-CSS fuer das Card-Grid — Spaltenzahl ueber die
    CSS-Variable `--mn-card-grid-cols` (Default 3 als Fallback).
    """
    return """
.mn-card-grid {
  display: grid;
  grid-template-columns: repeat(var(--mn-card-grid-cols, 3), 1fr);
  gap: 1rem;
}
""".strip()
