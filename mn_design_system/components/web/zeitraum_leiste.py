"""Web-Renderer Zeitraum-Leiste — HTML + CSS, 0.18.0.

Konsumiert ZeitraumLeisteInput aus `_patterns.contracts`. Segment-Leiste aus Links
(``?tage=30|90|365``): ein ``<nav>``, je Option ein ``<a>``, die gewaehlte Option traegt
``aria-current="page"``. Die Leiste hat kein Skript: jede Option ist eine Adresse, der
Zurueck-Knopf und das Lesezeichen funktionieren.

CSS-Strategie wie sub_nav: Masse, Schriftgroessen und Linien aus Web-Foundation-Tokens
(var(--web-*) / var(--space-*)), Farben aus `color.light.*`. Der aktive Zustand haengt
allein am Attribut ``aria-current`` — eine Wahrheit fuer Bildschirmleser und Auge.
Touch-Ziel: jede Option ist mindestens ``web.touch-target`` (44 px) hoch und breit.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import ZeitraumLeisteInput


def render_zeitraum_leiste_html(
    input: ZeitraumLeisteInput, *, inline_css: bool = False
) -> str:
    """Zeitraum-Leiste als HTML-Snippet (<nav> mit <a>-Optionen).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_zeitraum_leiste_css()}</style>")

    aria_label = escape(input.aria_label, quote=True)
    parts.append(f'<nav class="mn-zeitraum-leiste" aria-label="{aria_label}">')
    for option in input.optionen:
        aria_current = ' aria-current="page"' if option.active else ""
        href = escape(option.href, quote=True)
        label = escape(option.label)
        parts.append(
            f'<a class="mn-zeitraum-leiste__option" href="{href}"{aria_current}>'
            f"{label}</a>"
        )
    parts.append("</nav>")
    return "".join(parts)


def render_zeitraum_leiste_css() -> str:
    """Komponenten-CSS — Segment-Leiste, Token-Werte via Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--web-touch-target)` etc. greift. Die Leiste setzt keinen Aussenabstand: den
    bestimmt der Konsument.

    ``:hover`` steht VOR ``[aria-current="page"]`` (gleiche Spezifitaet, die spaetere
    Regel gewinnt): die gewaehlte Option bleibt auch unter dem Zeiger die gewaehlte.
    """
    return """
.mn-zeitraum-leiste {
  display: inline-flex;
  max-width: 100%;
  background: var(--color-light-surface, #ffffff);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-subtle, 2px);
  overflow: hidden;
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-zeitraum-leiste__option {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--web-touch-target, 44px);
  min-width: var(--web-touch-target, 44px);
  padding: 0 var(--space-4, 16px);
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  font-weight: 500;
  white-space: nowrap;
  text-decoration: none;
  color: var(--color-light-text-muted, #6b7280);
  border-right: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
}
.mn-zeitraum-leiste__option:last-child {
  border-right: 0;
}
.mn-zeitraum-leiste__option:hover {
  background: var(--color-light-surface-subtle, #f6f6f6);
  color: var(--color-light-text, #1e1b4b);
}
.mn-zeitraum-leiste__option[aria-current="page"] {
  background: var(--color-indigo-50, #eef2ff);
  color: var(--color-light-accent, #4F46E5);
}
.mn-zeitraum-leiste__option:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: calc(var(--web-stroke-focus, 2px) * -1);
}
""".strip()
