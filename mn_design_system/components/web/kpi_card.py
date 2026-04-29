"""Web-Renderer KPI-Card — HTML + CSS, Welle E.0 (S238).

Konsumiert KpiCardInput aus `_patterns.contracts`. Liefert ein HTML-Snippet
plus optional embedbares CSS.

CSS-Strategie:
- Token-Werte kommen aus `dist/css/tokens.css` (CSS Custom Properties),
  die vom Konsumenten in `<head>` eingebunden werden muss.
- Komponenten-Layout (Grid, Padding, Schriftgroessen) liefert
  `render_kpi_card_css()`. Konsument kann das einmal cachen.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
    SparklineInput,
)
from mn_design_system.components.web.sparkline import render_sparkline_svg

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

    parts.append('<article class="mn-kpi-card">')
    parts.append(f'<div class="mn-kpi-card__label">{label}</div>')
    parts.append(f'<div class="mn-kpi-card__value">{value}</div>')

    if input.change_pct is not None:
        sign = "+" if input.change_pct > 0 else ""
        change_str = escape(f"{sign}{input.change_pct:.2f}%")
        parts.append(
            f'<div class="mn-kpi-card__change {trend_class}">{trend_glyph} {change_str}</div>'
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


def render_kpi_card_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` in seinen Build-Output einbinden,
    damit `var(--color-light-text)` etc. greift.
    """
    return """
.mn-kpi-card {
  display: grid;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: var(--color-light-surface, #ffffff);
  border: 1px solid var(--color-light-border, #cbd5e1);
  border-radius: var(--radius-card, 6px);
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
}
.mn-kpi-card__label {
  font-size: 0.6875rem; /* ~9pt */
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-light-text-muted, #6b7280);
}
.mn-kpi-card__value {
  font-size: 1rem; /* ~10pt */
  font-weight: 700;
  color: var(--color-light-h1, #312e81);
  line-height: 1.2;
}
.mn-kpi-card__change {
  font-size: 0.55rem; /* ~8pt */
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
.mn-kpi-card__sparkline {
  margin: 0.125rem 0;
  line-height: 0;
}
.mn-kpi-card__caption {
  font-size: 0.4375rem; /* ~7pt */
  font-style: italic;
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
