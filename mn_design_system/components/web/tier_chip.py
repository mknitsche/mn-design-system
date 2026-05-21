"""Web-Renderer Tier-Chip — HTML + CSS, UX-Welle v0.2.

Konsumiert TierChipInput aus `_patterns.contracts`. Primitiv-Baustein: ein
einzelnes `<span>`, tier-getoent.

CSS-Strategie: alle Masse, Schriftgroessen und Linien aus Web-Foundation-Tokens
(var(--web-*) / var(--space-*)). Die Tier-Toene bleiben CSS Custom Properties —
pro Tier eine Modifier-Klasse, kein Inline-Hex.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import TierChipInput, WebTier

_TIERS: tuple[WebTier, ...] = (
    WebTier.BIBLIOTHEK,
    WebTier.ATELIER,
    WebTier.KABINETT,
    WebTier.START,
)


def render_tier_chip_html(input: TierChipInput, *, inline_css: bool = False) -> str:
    """Tier-Chip als HTML-Snippet (ein <span>).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    classes = ["mn-tier-chip", f"mn-tier-chip--{input.tier.value}"]
    if input.bordered:
        classes.append("mn-tier-chip--bordered")

    label = escape(input.label)

    parts = []
    if inline_css:
        parts.append(f"<style>{render_tier_chip_css()}</style>")

    parts.append(f'<span class="{" ".join(classes)}">{label}</span>')
    return "".join(parts)


def render_tier_chip_css() -> str:
    """Komponenten-CSS — Layout + 4 Tier-Modifier, Token-Werte via Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-tier-bibliothek-bg)` etc. greift.
    """
    rules = [
        """
.mn-tier-chip {
  display: inline-block;
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border-radius: var(--radius-subtle, 2px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  font-weight: 600;
  cursor: default;
}
.mn-tier-chip--bordered {
  border: var(--web-stroke-line, 1px) solid transparent;
}
.mn-tier-chip--loading {
  background: var(--color-light-surface-subtle, #f6f6f6);
  color: var(--color-light-text-muted, #6b7280);
  font-style: italic;
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        rules.append(
            f".mn-tier-chip--{t} {{\n"
            f"  background: var(--color-tier-{t}-bg, #f0fdf4);\n"
            f"  color: var(--color-tier-{t}-text, #166534);\n"
            f"}}"
        )
        rules.append(
            f".mn-tier-chip--{t}.mn-tier-chip--bordered {{\n"
            f"  border-color: var(--color-tier-{t}-border, #bbf7d0);\n"
            f"}}"
        )
    return "\n".join(rules)
