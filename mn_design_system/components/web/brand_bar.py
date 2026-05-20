"""Web-Renderer Brand-Bar — HTML + CSS, UX-Welle v0.2.

Konsumiert BrandBarInput aus `_patterns.contracts`. L2 der 3-Layer-Affordance
(Spec §A4): Brand-Text plus 0-3 Status-Chips (Page-Tier, User-Tier). Affordance:
Info, nicht klickbar.

Bettet den Tier-Chip-Renderer ein (`render_tier_chip_html` mit `bordered=True`).
CSS-Strategie wie kpi_card / wetter_strip: Token-Werte via CSS Custom Properties,
Komponenten-CSS liefert `render_brand_bar_css()`. Der inline_css-Pfad gibt
Brand-Bar-CSS UND Tier-Chip-CSS aus (Chips sind eingebettet).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import BrandBarInput, TierChipInput
from mn_design_system.components.web.tier_chip import (
    render_tier_chip_css,
    render_tier_chip_html,
)


def render_brand_bar_html(input: BrandBarInput, *, inline_css: bool = False) -> str:
    """Brand-Bar als HTML-Snippet.

    inline_css=True hangt Brand-Bar-CSS und Tier-Chip-CSS in einem
    <style>-Block an — fuer Single-Snippet-Embeds.
    """
    brand_text = escape(input.brand_text)

    parts = []
    if inline_css:
        parts.append(
            f"<style>{render_brand_bar_css()}\n{render_tier_chip_css()}</style>"
        )

    parts.append('<header class="mn-brand-bar">')
    parts.append(f'<span class="mn-brand-bar__brand">{brand_text}</span>')

    parts.append('<div class="mn-brand-bar__chips">')
    for chip in input.chips:
        parts.append(
            render_tier_chip_html(
                TierChipInput(tier=chip.tier, label=chip.label, bordered=True)
            )
        )
    if input.user_chip_id is not None:
        parts.append(
            f'<span id="{escape(input.user_chip_id, quote=True)}" '
            f'class="mn-tier-chip mn-tier-chip--loading">'
            f"{escape(input.user_chip_label)}</span>"
        )
    parts.append("</div>")

    parts.append("</header>")
    return "".join(parts)


def render_brand_bar_css() -> str:
    """Komponenten-CSS — Layout-only. Chip-CSS kommt aus render_tier_chip_css().

    Konsument muss `dist/css/tokens.css` einbinden.
    """
    return """
.mn-brand-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--color-light-surface, #ffffff);
  border-bottom: 1px solid var(--color-light-border, #cbd5e1);
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
}
.mn-brand-bar__brand {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-light-h1, #312e81);
}
.mn-brand-bar__chips {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
""".strip()
