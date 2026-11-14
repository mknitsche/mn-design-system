"""Web-Renderer Kachel — HTML + CSS, 0.24.0 (Welle 1 „Rahmen und Foyer“).

Konsumiert KachelInput aus `_patterns.contracts`: Kicker (zugleich Ueberschrift, `<h3>`),
optional grosse Zahl, Inhalt, Stand-Zeile und Fusslink. Das Raster `mn-kachel-raster` hat eine
Spalte und ab `web.layout.bp-tablet` zwei; es loest das feste `900px` der heutigen Startseite ab.

`inhalt_html` wird NICHT escapt (Markup aus anderen DS-Renderern, Regel P11): der Konsument setzt
jeden Text darin mit `html.escape(text, quote=True)` ein. Alle anderen Felder escapt der Renderer.
CSS-Strategie: nur var(--…) mit Rueckfall, keine Literalfarbe, keine rohen Masse.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import KachelInput
from mn_design_system.tokens import get


def render_kachel_html(input: KachelInput, *, inline_css: bool = False) -> str:
    """Kachel als `<section class="mn-kachel" aria-labelledby=…>`."""
    titel_id = escape(input.titel_id, quote=True)
    teile = [
        f'<section class="mn-kachel" aria-labelledby="{titel_id}">',
        f'<h3 id="{titel_id}" class="mn-kachel__kicker">{escape(input.kicker)}</h3>',
    ]
    if input.display_zahl is not None:
        teile.append(f'<p class="mn-kachel__zahl">{escape(input.display_zahl)}</p>')
    teile.append(f'<div class="mn-kachel__inhalt">{input.inhalt_html}</div>')
    if input.stand is not None:
        teile.append(f'<p class="mn-kachel__stand">{escape(input.stand)}</p>')
    if input.fuss_link is not None:
        href, label = input.fuss_link
        teile.append(
            f'<a class="mn-kachel__fuss" href="{escape(href, quote=True)}">{escape(label)}</a>'
        )
    teile.append("</section>")
    html = "".join(teile)
    if inline_css:
        return f"<style>{render_kachel_css()}</style>{html}"
    return html


def render_kachel_css() -> str:
    """Komponenten-CSS — Kachel und Raster `mn-kachel-raster`."""
    bp_tablet = get("web.layout.bp-tablet")
    return f"""
.mn-kachel-raster {{
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-4, 16px);
}}
@media (min-width: {bp_tablet}) {{
  .mn-kachel-raster {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
}}
.mn-kachel {{
  display: flex;
  flex-direction: column;
  gap: var(--space-2, 8px);
  box-sizing: border-box;
  padding: var(--space-4, 16px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text, #1e1b4b);
  background: var(--color-light-surface, #ffffff);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-subtle, 2px);
}}
.mn-kachel__kicker {{
  margin: 0;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-light-text-muted, #6b7280);
}}
.mn-kachel__zahl {{
  margin: 0;
  font-size: var(--web-text-h2, 28px);
  line-height: var(--web-leading-h2, 1.22);
  font-weight: 600;
  color: var(--color-light-h1, #312e81);
}}
.mn-kachel__inhalt {{
  min-width: 0;
}}
.mn-kachel__stand {{
  margin: 0;
  font-size: var(--web-text-caption, 12px);
  color: var(--color-light-text-muted, #6b7280);
}}
.mn-kachel__fuss {{
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  min-height: var(--web-touch-target, 44px);
  color: var(--color-light-accent, #4F46E5);
  text-decoration: none;
}}
.mn-kachel__fuss:hover {{
  text-decoration: underline;
}}
.mn-kachel__fuss:focus-visible {{
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}}
""".strip()
