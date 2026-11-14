"""Web-Renderer Status-Punkt — HTML + CSS, 0.24.0 (Welle 1).

Konsumiert StatusPunktInput: Symbol UND Wort, nie Farbe allein. Die Stufen unterscheiden sich
durch Form des Symbols (✓ ▲ ✕ –) und Hintergrund, nicht nur durch den Farbton; das Wort steht
immer im Text. Farben aus den Status-Tokens, Text in der Standard-Textfarbe (Kontrast).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import StatusPunktInput
from mn_design_system.tokens import get

_SYMBOL = {"ok": "✓", "warn": "▲", "alarm": "✕", "unbekannt": "–"}


def render_status_punkt_html(
    input: StatusPunktInput, *, inline_css: bool = False
) -> str:
    """Status-Punkt als `<span class="mn-status mn-status--<stufe>">` mit Symbol und Wort."""
    html = (
        f'<span class="mn-status mn-status--{input.stufe}">'
        f'<span class="mn-status__symbol" aria-hidden="true">{_SYMBOL[input.stufe]}</span> '
        f'<span class="mn-status__wort">{escape(input.wort)}</span></span>'
    )
    if inline_css:
        return f"<style>{render_status_punkt_css()}</style>{html}"
    return html


def render_status_punkt_css() -> str:
    """Komponenten-CSS — vier Stufen, Farben aus `color.status.*`."""
    stufen = {
        # stufe: (Symbolfarbe, Hintergrund, Rand)
        "ok": ("success", "success-bg", "success"),
        "warn": ("urgent", "warning-bg", "warning"),
        "alarm": ("error", "error-bg", "error"),
    }
    regeln = [
        """
.mn-status {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  padding: 0 var(--space-2, 8px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  font-weight: 500;
  color: var(--color-light-text, #1e1b4b);
  background: var(--color-light-surface-subtle, #f6f6f6);
  border: var(--web-stroke-line, 1px) solid var(--color-light-border, #d1d5db);
  border-radius: var(--radius-round, 9999px);
}
.mn-status__symbol {
  font-weight: 700;
  color: var(--color-light-text-muted, #6b7280);
}"""
    ]
    for stufe, (symbol, bg, rand) in stufen.items():
        regeln.append(
            f".mn-status--{stufe} {{\n"
            f"  background: var(--color-status-{bg}, {get(f'color.status.{bg}')});\n"
            f"  border-color: var(--color-status-{rand}, {get(f'color.status.{rand}')});\n"
            f"}}\n"
            f".mn-status--{stufe} .mn-status__symbol {{\n"
            f"  color: var(--color-status-{symbol}, {get(f'color.status.{symbol}')});\n"
            f"}}"
        )
    return "\n".join(regeln)
