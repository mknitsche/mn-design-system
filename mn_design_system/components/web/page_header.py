"""Web-Renderer Page-Header — HTML + CSS, UX-Welle v0.2.

Konsumiert PageHeaderInput aus `_patterns.contracts`. Seiten-Kopf einer
mkn-desk.com-Seite: H1-Titel plus optionaler Lead-Absatz.

CSS-Strategie wie kpi_card / wetter_strip: Farb- und Schrift-Token via CSS
Custom Properties, Layout-Werte (Schriftgroessen in rem, Abstaende) inline.
Schriftgroessen bewusst in rem statt `var(--font-size-*)`: die `font.size.*`-
Tokens sind print-orientiert (pt). Web nutzt rem — konsistent mit den
bestehenden Web-Renderern (kpi_card, wetter_strip). Eine web-spezifische
font.size-Familie waere eine eigene Token-Welle.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import PageHeaderInput


def render_page_header_html(
    input: PageHeaderInput, *, inline_css: bool = False
) -> str:
    """Page-Header als HTML-Snippet (<header> mit <h1> und optionalem Lead).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_page_header_css()}</style>")

    parts.append('<header class="mn-page-header">')
    parts.append(
        f'<h1 class="mn-page-header__title">{escape(input.title)}</h1>'
    )
    if input.lead is not None:
        parts.append(
            f'<p class="mn-page-header__lead">{escape(input.lead)}</p>'
        )
    parts.append("</header>")
    return "".join(parts)


def render_page_header_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-light-h1)` etc. greift.
    """
    return """
.mn-page-header {
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
  margin-bottom: 1.5rem;
}
.mn-page-header__title {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0;
  color: var(--color-light-h1, #312e81);
}
.mn-page-header__lead {
  font-size: 1rem;
  line-height: 1.5;
  margin: 0.5rem 0 0;
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
