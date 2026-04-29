"""Web-Renderer Wetter-Strip — HTML + CSS, Welle E.0 (S238).

Konsumiert WetterStripInput aus `_patterns.contracts`. Liefert HTML-Tabelle mit
Phosphor-Icon-Web-Font (CDN oder selbst gehostet) plus optional Komponenten-CSS.

Konsumenten-Voraussetzung: Phosphor Web-Font einbinden, z.B.
    <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.x/src/regular/style.css">
oder selbst-gehostet aus dem Submodul-Font-Verzeichnis.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import (
    WetterCategory,
    WetterStripInput,
)

# Mapping auf Phosphor-Icon-Klassen (Web-Font-Variante).
# Symmetrisch zur PDF-Implementation (build_wetter_strip in pdf/wetter_strip.py).
_ICON_CLASS = {
    WetterCategory.SONNIG: "ph-sun",
    WetterCategory.HEITER: "ph-cloud-sun",
    WetterCategory.BEWOELKT: "ph-cloud",
    WetterCategory.REGEN: "ph-cloud-rain",
    WetterCategory.SCHNEE: "ph-cloud-snow",
    WetterCategory.GEWITTER: "ph-cloud-lightning",
    WetterCategory.NEBEL: "ph-cloud-fog",
    WetterCategory.WIND: "ph-wind",
}


def render_wetter_strip_html(input: WetterStripInput, *, inline_css: bool = False) -> str:
    """Wetter-Strip als HTML-Tabelle.

    inline_css=True embedbar fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_wetter_strip_css()}</style>")

    location = escape(input.location)
    parts.append(f'<section class="mn-wetter-strip" aria-label="Wetter {location}">')
    parts.append(f'<header class="mn-wetter-strip__header">{location}</header>')

    parts.append('<table class="mn-wetter-strip__grid">')
    parts.append("<thead><tr>")
    for day in input.days:
        parts.append(
            f'<th scope="col" class="mn-wetter-strip__day-label">{escape(day.header_label)}</th>'
        )
    parts.append("</tr></thead>")

    parts.append("<tbody>")
    parts.append("<tr>")
    for day in input.days:
        icon_class = _ICON_CLASS[day.category]
        parts.append(
            f'<td class="mn-wetter-strip__icon">'
            f'<i class="ph {icon_class}" aria-hidden="true"></i>'
            f'<span class="mn-wetter-strip__sr">{escape(day.category.value)}</span>'
            f"</td>"
        )
    parts.append("</tr>")

    parts.append("<tr>")
    for day in input.days:
        parts.append(
            f'<td class="mn-wetter-strip__temp">'
            f'<span class="mn-wetter-strip__tmax">{day.temp_max_c}°</span>'
            f'<span class="mn-wetter-strip__tmin"> / {day.temp_min_c}°</span>'
            f"</td>"
        )
    parts.append("</tr>")

    parts.append("<tr>")
    for day in input.days:
        parts.append(f'<td class="mn-wetter-strip__precip">{day.precip_pct}%</td>')
    parts.append("</tr>")
    parts.append("</tbody>")
    parts.append("</table>")

    if input.summary_text:
        summary = escape(input.summary_text)
        parts.append(f'<p class="mn-wetter-strip__summary">{summary}</p>')

    parts.append("</section>")
    return "".join(parts)


def render_wetter_strip_css() -> str:
    """Komponenten-CSS fuer den Wetter-Strip."""
    return """
.mn-wetter-strip {
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
  color: var(--color-light-text, #1e1b4b);
}
.mn-wetter-strip__header {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-light-text-muted, #6b7280);
  margin-bottom: 0.25rem;
}
.mn-wetter-strip__grid {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
.mn-wetter-strip__day-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-align: center;
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--color-light-border, #cbd5e1);
}
.mn-wetter-strip__icon {
  font-size: 1.25rem;
  text-align: center;
  padding: 0.375rem 0;
  color: var(--color-light-h2, #4338ca);
}
.mn-wetter-strip__sr {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
.mn-wetter-strip__temp {
  font-size: 0.75rem;
  text-align: center;
  padding: 0.125rem 0;
}
.mn-wetter-strip__tmax {
  font-weight: 700;
  color: var(--color-light-h1, #312e81);
}
.mn-wetter-strip__tmin {
  color: var(--color-light-text-muted, #6b7280);
}
.mn-wetter-strip__precip {
  font-size: 0.625rem;
  text-align: center;
  color: var(--color-status-success, #2e7d32);
  padding-bottom: 0.25rem;
}
.mn-wetter-strip__summary {
  margin-top: 0.5rem;
  font-size: 0.6875rem;
  font-style: italic;
  color: var(--color-light-text-muted, #6b7280);
  line-height: 1.4;
}
""".strip()
