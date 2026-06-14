"""Web-Renderer Source-Ref — HTML + CSS, Briefing-Web-Ausgabe (Welle 3).

Konsumiert SourceRefInput aus `_patterns.contracts`. Macht die Quelle zu einem
erstklassigen Baustein: "Quelle: <a>label ↗</a>", optional gefolgt von
"· weitere: <a>… ↗</a> · …". Klein und grau wie die Meta-Feinzeile.

CSS-Strategie: alle Masse, Schriftgroessen und Farben aus Web-Foundation- bzw.
Light-Tokens (var(--web-*) / var(--color-light-*)). Der externe-Link-Pfeil (↗)
kommt — wie im Mockup (.src::after) — per CSS-`::after`, nicht als Text, damit
Inhalt und Dekoration getrennt bleiben.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import (
    SourceLink,
    SourceRefInput,
)


def _link_html(link: SourceLink) -> str:
    """Eine Quelle als <a> — href quote-escaped, Label text-escaped.

    Der ↗-Pfeil wird per CSS (.mn-source-ref__link::after) angehaengt.
    """
    href = escape(link.href, quote=True)
    label = escape(link.label)
    return f'<a class="mn-source-ref__link" href="{href}">{label}</a>'


def render_source_ref_html(input: SourceRefInput, *, inline_css: bool = False) -> str:
    """Quelle(n) als Inline-HTML-Snippet (<span class="mn-source-ref">).

    "Quelle: <primary>" und — falls `weitere` gesetzt — " · weitere: <w1> · <w2>".
    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_source_ref_css()}</style>")

    parts.append('<span class="mn-source-ref">')
    parts.append(f"Quelle: {_link_html(input.primary)}")
    if input.weitere:
        weitere = " · ".join(_link_html(link) for link in input.weitere)
        parts.append(f" · weitere: {weitere}")
    parts.append("</span>")
    return "".join(parts)


def render_source_ref_css() -> str:
    """Komponenten-CSS — kleine graue Meta-Optik, Token-Werte via Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-light-text-muted)` etc. greift.
    """
    return """
.mn-source-ref {
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-source-ref__link {
  font-weight: 500;
  color: var(--color-light-text-muted, #6b7280);
  text-decoration: none;
}
.mn-source-ref__link:hover {
  text-decoration: underline;
}
.mn-source-ref__link:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
.mn-source-ref__link::after {
  content: " \\2197";
}
""".strip()
