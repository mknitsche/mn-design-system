"""Web-Renderer Zurueck-Zeile — HTML + CSS, 0.19.0 (claudeAI TODO-885 Ordnung 2).

Konsumiert BackLinkInput aus `_patterns.contracts`. Die EINE Zurueck-Zeile einer
mkn-desk.com-Seite unterhalb einer Reiterseite: ein Link auf die Elternseite.

CSS-Strategie: nur var(--…) mit Rueckfall — Schrift, Farbe, Touch-Ziel, Abstand und
Fokus-Ring aus den Web-Foundation- und Farb-Tokens, keine Literalfarbe.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import BackLinkInput


def render_back_link_html(input: BackLinkInput, *, inline_css: bool = False) -> str:
    """Zurueck-Zeile als HTML-Snippet (ein <nav> mit einem <a>).

    Der Pfeil ist reine Zierde (`aria-hidden`); der Link-Text ist der Titel der
    Elternseite. inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_back_link_css()}</style>")
    parts.append(
        '<nav class="mn-back-link" aria-label="Zurück">'
        f'<a href="{escape(input.href, quote=True)}">'
        f'<span aria-hidden="true">←</span> {escape(input.label)}'
        "</a></nav>"
    )
    return "".join(parts)


def render_back_link_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties."""
    return """
.mn-back-link {
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-ui, 14px);
  margin-bottom: var(--space-4, 16px);
}
.mn-back-link a {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  min-height: var(--web-touch-target, 44px);
  color: var(--color-light-text-muted, #6b7280);
  text-decoration: none;
}
.mn-back-link a:hover {
  color: var(--color-light-accent, #4F46E5);
}
.mn-back-link a:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
""".strip()
