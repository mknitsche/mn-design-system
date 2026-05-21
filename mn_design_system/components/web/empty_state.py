"""Web-Renderer Empty-State — HTML + CSS, UX-Welle B (v0.9.0).

Konsumiert EmptyStateInput. Ein ruhiger Leer-Zustand-Block: gedämpfter Text,
kein greller Kasten. Optionale Tier-Verankerung über eine zarte Akzent-Border.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import EmptyStateInput, WebTier

_TIERS: tuple[WebTier, ...] = (
    WebTier.BIBLIOTHEK,
    WebTier.ATELIER,
    WebTier.KABINETT,
    WebTier.START,
)


def render_empty_state_html(input: EmptyStateInput, *, inline_css: bool = False) -> str:
    classes = ["mn-empty-state"]
    if input.tier is not None:
        classes.append(f"mn-empty-state--{input.tier.value}")

    parts = []
    if inline_css:
        parts.append(f"<style>{render_empty_state_css()}</style>")
    parts.append(f'<div class="{" ".join(classes)}">')
    parts.append(f'<p class="mn-empty-state__message">{escape(input.message)}</p>')
    parts.append("</div>")
    return "".join(parts)


def render_empty_state_css() -> str:
    rules = [
        """
.mn-empty-state {
  padding: var(--space-6, 24px) var(--space-5, 20px);
  border-radius: var(--radius-subtle, 2px);
  background: var(--color-light-surface-subtle, #f6f6f6);
  border-left: var(--web-stroke-line-strong, 2px) solid var(--web-color-separator, #b4bcc8);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-empty-state__message {
  margin: 0;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        rules.append(
            f".mn-empty-state--{t} {{\n"
            f"  border-left-color: var(--color-tier-{t}-border, #cbd5e1);\n"
            f"}}"
        )
    return "\n".join(rules)
