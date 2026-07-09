"""Web-Renderer Status-Banner — HTML + CSS, Twin-Chat (Build-Spec cld1-S57, T-3.4).

Konsumiert StatusBannerInput aus `_patterns.chat_contracts`. Eine schmale,
einzeilige Statuszeile ueber dem Chat-Verlauf (kein grosser Alert-Kasten —
Tufte: Signal aus Farbdosis + Struktur, nicht aus Flaeche). Vier Zustaende:

- locked        — Sitzung gesperrt, Passkey erforderlich (Server-Startwert).
- unlocked      — Zweitfaktor bestaetigt, Chat nutzbar.
- budget-block  — Tages-Budget erreicht (Server lehnt weitere Turns ab).
- error         — Transport-/Runner-Fehler.

chat.js aktualisiert `state`-Modifier-Klasse + Text laufend (z.B. nach
GET /api/me oder einem SSE `error`-Event).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.chat_contracts import (
    StatusBannerInput,
    StatusBannerState,
)

_STATES: tuple[StatusBannerState, ...] = (
    StatusBannerState.LOCKED,
    StatusBannerState.UNLOCKED,
    StatusBannerState.BUDGET_BLOCK,
    StatusBannerState.ERROR,
)

# Je Zustand: (Punkt-Variable, Punkt-Fallback, Text-Variable, Text-Fallback).
# Referenziert die BESTEHENDE color.status.*/color.accent.warm.*-Familie
# (schon anderswo im DS genutzt, z.B. kpi_card.py is_up/is_down) statt eine
# parallele Taxonomie zu erfinden — HC-7 (Standards sind Input, nicht Ziel:
# hier passt die vorhandene Status-Farbfamilie exakt).
_STATE_FALLBACK: dict[StatusBannerState, tuple[str, str, str, str]] = {
    StatusBannerState.LOCKED: (
        "--color-light-text-muted",
        "#6b7280",
        "--color-light-text-muted",
        "#6b7280",
    ),
    StatusBannerState.UNLOCKED: (
        "--color-status-success",
        "#2e7d32",
        "--color-status-success",
        "#2e7d32",
    ),
    StatusBannerState.BUDGET_BLOCK: (
        "--color-status-warning",
        "#f59e0b",
        "--color-accent-warm-text",
        "#78350f",
    ),
    StatusBannerState.ERROR: (
        "--color-status-error",
        "#D32F2F",
        "--color-status-error",
        "#D32F2F",
    ),
}


def render_status_banner_html(
    input: StatusBannerInput, *, inline_css: bool = False
) -> str:
    """Status-Banner als HTML-Snippet (<div role="status">).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_status_banner_css()}</style>")

    banner_id = escape(input.banner_id, quote=True)
    parts.append(
        f'<div class="mn-status-banner mn-status-banner--{input.state.value}" '
        f'id="{banner_id}" role="status" aria-live="polite">'
    )
    parts.append('<span class="mn-status-banner__dot" aria-hidden="true"></span>')
    parts.append(f'<span class="mn-status-banner__text">{escape(input.message)}</span>')
    parts.append("</div>")
    return "".join(parts)


def render_status_banner_css() -> str:
    """Komponenten-CSS — Layout + 4 Zustands-Modifier, Token-Werte via Custom Properties."""
    rules = [
        """
.mn-status-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2, 8px);
  padding: var(--space-2, 8px) var(--web-layout-page-inset, 44px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-caption, 12px);
  font-weight: 600;
  border-bottom: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
}
.mn-status-banner__dot {
  width: 0.55em;
  height: 0.55em;
  border-radius: var(--radius-round, 9999px);
  background: currentColor;
  flex: 0 0 auto;
}
.mn-status-banner__text {
  color: inherit;
}
""".strip()
    ]
    for state in _STATES:
        s = state.value
        dot_var, dot_fb, text_var, text_fb = _STATE_FALLBACK[state]
        rules.append(
            f".mn-status-banner--{s} {{\n  color: var({text_var}, {text_fb});\n}}"
        )
        rules.append(
            f".mn-status-banner--{s} .mn-status-banner__dot {{\n"
            f"  background: var({dot_var}, {dot_fb});\n"
            f"}}"
        )
    return "\n".join(rules)
