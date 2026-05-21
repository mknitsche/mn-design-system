"""Web-Renderer Page-Header — HTML + CSS, UX-Welle v0.2.

Konsumiert PageHeaderInput aus `_patterns.contracts`. Seiten-Kopf einer
mkn-desk.com-Seite: H1-Titel plus optionaler Lead-Absatz.

CSS-Strategie: alle Schriftgroessen, Zeilenhoehen und Abstaende aus
Web-Foundation-Tokens (var(--web-text-*) / var(--web-leading-*) /
var(--space-*)). Der Titel nutzt web.text.h1, der Lead web.text.lead.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import PageHeaderInput


def render_page_header_html(input: PageHeaderInput, *, inline_css: bool = False) -> str:
    """Page-Header als HTML-Snippet (<header> mit <h1> und optionalem Lead).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_page_header_css()}</style>")

    parts.append('<header class="mn-page-header">')
    parts.append(f'<h1 class="mn-page-header__title">{escape(input.title)}</h1>')
    if input.lead is not None:
        parts.append(f'<p class="mn-page-header__lead">{escape(input.lead)}</p>')
    parts.append("</header>")
    return "".join(parts)


def render_page_header_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-light-h1)` etc. greift.
    """
    return """
.mn-page-header {
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  margin-bottom: var(--space-6, 24px);
}
.mn-page-header__title {
  font-size: var(--web-text-h1, 33px);
  line-height: var(--web-leading-h1, 1.18);
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--color-light-h1, #312e81);
}
.mn-page-header__lead {
  font-size: var(--web-text-lead, 19px);
  line-height: var(--web-leading-lead, 1.55);
  margin: var(--space-2, 8px) 0 0;
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
