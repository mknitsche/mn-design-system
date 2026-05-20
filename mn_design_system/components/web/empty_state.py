"""Web-Renderer Empty-State — HTML + CSS, UX-Welle B (v0.9.0).

Konsumiert EmptyStateInput. Ein ruhiger Leer-Zustand-Block: gedämpfter Text,
kein greller Kasten. Optionale Tier-Verankerung über eine zarte Akzent-Border.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import EmptyStateInput


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
  padding: 1.75rem 1.25rem;
  border-radius: var(--radius-subtle, 2px);
  background: var(--color-light-surface-subtle, #f6f6f6);
  border-left: 3px solid var(--color-light-border, #cbd5e1);
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
}
.mn-empty-state__message {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-light-text-muted, #6b7280);
}
""".strip()
    ]
    for tier in ("bibliothek", "atelier", "kabinett", "start"):
        rules.append(
            f".mn-empty-state--{tier} {{\n"
            f"  border-left-color: var(--color-tier-{tier}-border, #cbd5e1);\n"
            f"}}"
        )
    return "\n".join(rules)
