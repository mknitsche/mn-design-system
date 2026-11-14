"""Web-Renderer Ortszeile — HTML + CSS, 0.24.0 (Welle 1 „Rahmen und Foyer“).

Konsumiert OrtszeileInput aus `_patterns.contracts`. Die Kette „Raum › Bereich › Seite“ als
einzeilige Link-Reihe; das LETZTE Glied ist die Elternseite und beginnt mit „← “. Am schmalen
Bildschirm kuerzen die vorderen Glieder mit Auslassungszeichen, das letzte Glied schrumpft nie.

Ersetzt `back_link` und `pfad_zeile` nicht — beide bleiben unveraendert (additiv).
CSS-Strategie: nur var(--…) mit Rueckfall, keine Literalfarbe, keine rohen Masse.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import OrtszeileInput


def render_ortszeile_html(input: OrtszeileInput, *, inline_css: bool = False) -> str:
    """Ortszeile als <nav><ol><li><a>…; das letzte Glied traegt `mn-ortszeile__eltern`."""
    letztes = len(input.glieder) - 1
    items = []
    for i, (href, label) in enumerate(input.glieder):
        ziel = escape(href, quote=True)
        if i == letztes:
            items.append(
                f'<li><a class="mn-ortszeile__eltern" href="{ziel}">'
                f"← {escape(label)}</a></li>"
            )
        else:
            items.append(f'<li><a href="{ziel}">{escape(label)}</a></li>')
    html = f'<nav class="mn-ortszeile" aria-label="Ort"><ol>{"".join(items)}</ol></nav>'
    if inline_css:
        return f"<style>{render_ortszeile_css()}</style>{html}"
    return html


def render_ortszeile_css() -> str:
    """Komponenten-CSS — einzeilig, Kuerzung von vorn, letztes Glied unkuerzbar."""
    return """
.mn-ortszeile {
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-ortszeile ol {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  margin: 0;
  padding: 0;
  list-style: none;
}
.mn-ortszeile li {
  display: flex;
  align-items: center;
  white-space: nowrap;
}
.mn-ortszeile li:not(:last-child) {
  flex: 0 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mn-ortszeile li:last-child {
  flex: none;
}
.mn-ortszeile li + li::before {
  content: "›" / "";
  padding-inline: var(--space-2, 8px);
}
.mn-ortszeile a {
  display: block;
  min-width: 0;
  line-height: var(--web-touch-target, 44px);
  color: var(--color-light-text-muted, #6b7280);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mn-ortszeile a:hover {
  color: var(--color-light-accent, #4F46E5);
  text-decoration: underline;
}
.mn-ortszeile a:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}
""".strip()
