"""Web-Renderer Footer — HTML + CSS, UX-Welle v0.2.

Konsumiert FooterInput aus `_patterns.contracts`. Seiten-Fuss von
mkn-desk.com: bis zu 3 Link-Spalten plus eine optionale Meta-Zeile
(Version + Copyright-Notiz).

CSS-Strategie wie kpi_card / wetter_strip: Farb- und Schrift-Token via CSS
Custom Properties, Layout-Werte (Grid, Schriftgroessen in rem) inline. Die
"Hochstrich"-Trennlinie ueber dem Footer ist eine duenne `border-top`
(Spec §cld1-S19 Variante E).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import FooterInput


def render_footer_html(input: FooterInput, *, inline_css: bool = False) -> str:
    """Footer als HTML-Snippet (<footer> mit Link-Spalten + optionaler Meta-Zeile).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_footer_css()}</style>")

    parts.append('<footer class="mn-footer">')
    parts.append('<div class="mn-footer__columns">')
    for column in input.columns:
        parts.append('<div class="mn-footer__col">')
        parts.append(
            f'<h2 class="mn-footer__col-title">{escape(column.title)}</h2>'
        )
        parts.append('<ul class="mn-footer__list">')
        for link in column.links:
            href = escape(link.href, quote=True)
            label = escape(link.label)
            parts.append(
                f'<li class="mn-footer__item">'
                f'<a class="mn-footer__link" href="{href}">{label}</a>'
                f"</li>"
            )
        parts.append("</ul>")
        parts.append("</div>")
    parts.append("</div>")

    if input.version is not None or input.note is not None:
        parts.append('<div class="mn-footer__meta">')
        if input.note is not None:
            parts.append(
                f'<span class="mn-footer__note">{escape(input.note)}</span>'
            )
        if input.version is not None:
            parts.append(
                f'<span class="mn-footer__version">{escape(input.version)}</span>'
            )
        parts.append("</div>")

    parts.append("</footer>")
    return "".join(parts)


def render_footer_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-light-border)` etc. greift.
    """
    return """
.mn-footer {
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
  padding-top: 1.5rem;
  border-top: var(--stroke-thin, 0.5pt) solid var(--color-light-border, #cbd5e1);
  color: var(--color-light-text, #1e1b4b);
}
.mn-footer__columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.mn-footer__col-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 0.5rem;
  color: var(--color-light-text-muted, #6b7280);
}
.mn-footer__list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.mn-footer__item {
  margin: 0.25rem 0;
}
.mn-footer__link {
  font-size: 0.8125rem;
  text-decoration: none;
  color: var(--color-light-text, #1e1b4b);
}
.mn-footer__link:hover {
  text-decoration: underline;
}
.mn-footer__link:focus-visible {
  outline: 2px solid var(--color-light-accent, #4F46E5);
  outline-offset: 2px;
}
.mn-footer__meta {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.5rem;
  font-size: 0.6875rem;
  color: var(--color-light-text-subtle, #9ca3af);
}
""".strip()
