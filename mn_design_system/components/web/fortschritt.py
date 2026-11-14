"""Web-Renderer Fortschritt — HTML + CSS, 0.24.0 (Welle 1).

Konsumiert FortschrittInput: ein Anteil 0..1 als `role="progressbar"` mit `aria-valuenow`.
Die Fuellung ist ein SVG-Rechteck (Breite als Zahl im `viewBox`), KEIN `style`-Attribut — die
Seite darf eine CSP ohne `style-src 'unsafe-inline'` haben.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import FortschrittInput


def render_fortschritt_html(
    input: FortschrittInput, *, inline_css: bool = False
) -> str:
    """Fortschritt als `<div class="mn-fortschritt" role="progressbar" …>`."""
    prozent = input.anteil * 100
    breite = f"{prozent:.2f}".rstrip("0").rstrip(".")
    lid = escape(input.label_id, quote=True)
    html = (
        f'<div class="mn-fortschritt" role="progressbar" aria-valuemin="0" '
        f'aria-valuemax="100" aria-valuenow="{round(prozent)}" aria-labelledby="{lid}">'
        f'<span id="{lid}" class="mn-fortschritt__label">{escape(input.label)}</span>'
        '<svg class="mn-fortschritt__balken" viewBox="0 0 100 1" '
        'preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        '<rect class="mn-fortschritt__spur" width="100" height="1"/>'
        f'<rect class="mn-fortschritt__fuellung" width="{breite}" height="1"/>'
        "</svg></div>"
    )
    if inline_css:
        return f"<style>{render_fortschritt_css()}</style>{html}"
    return html


def render_fortschritt_css() -> str:
    """Komponenten-CSS — Spur und Fuellung als SVG-`fill`, Hoehe aus `space.2`."""
    return """
.mn-fortschritt {
  display: flex;
  flex-direction: column;
  gap: var(--space-1, 4px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-fortschritt__balken {
  display: block;
  width: 100%;
  height: var(--space-2, 8px);
  border-radius: var(--radius-subtle, 2px);
}
.mn-fortschritt__spur {
  fill: var(--color-light-border-subtle, #e5e7eb);
}
.mn-fortschritt__fuellung {
  fill: var(--color-light-accent, #4F46E5);
}
""".strip()
