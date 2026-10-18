"""Web-Renderer Pfadzeile — HTML + CSS, 0.20.0 (Magazin-Welle 0).

Konsumiert PfadZeileInput aus `_patterns.contracts`. Die Vorfahren eines Ordners als Links
("archiv › briefing ›"), von oben nach unten. Welche Vorfahren gezeigt werden, entscheidet der
Konsument (im Magazin erst ab Ebene 3, ohne direkten Elternordner); bei leeren Vorfahren
entsteht kein Markup.

CSS-Strategie: nur var(--…) mit Rueckfall, keine Literalfarbe.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import PfadZeileInput


def render_pfad_zeile_html(p: PfadZeileInput, *, inline_css: bool = False) -> str:
    """Pfadzeile als <nav>; "" bei leeren Vorfahren. Trenner "›" ist reine Zierde."""
    if not p.vorfahren:
        return ""
    glieder = " ".join(
        f'<a href="{escape(href, quote=True)}">{escape(label)}</a> '
        '<span aria-hidden="true">›</span>'
        for label, href in p.vorfahren
    )
    html = f'<nav class="mn-pfad-zeile" aria-label="Pfad">{glieder}</nav>'
    if inline_css:
        return f"<style>{render_pfad_zeile_css()}</style>{html}"
    return html


def render_pfad_zeile_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties."""
    return """
.mn-pfad-zeile {
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-pfad-zeile a {
  color: var(--color-light-text-muted, #6b7280);
  text-decoration: none;
}
.mn-pfad-zeile a:hover {
  color: var(--color-light-accent, #4F46E5);
  text-decoration: underline;
}
.mn-pfad-zeile a:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}
""".strip()
