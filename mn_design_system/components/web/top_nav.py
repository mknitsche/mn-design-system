"""Web-Renderer Top-Nav — HTML + CSS, UX-Welle v0.2.

Konsumiert TopNavInput aus `_patterns.contracts`. L1 der 3-Layer-Affordance
(Spec §A4): Tier-Wechsel-Navigation. Transparente Pills auf dunklem Grund;
jeder Eintrag fuehrt in einen anderen Tier.

CSS-Verhalten (Spec §A4 L1):
- Dunkler Grund (`var(--color-dark-surface)`).
- Eintrag inaktiv: transparente Pill, nur Text.
- Hover inaktiv: weiss-Tint (`rgba(255,255,255,0.08)`) — neutral, weil die
  Top-Nav UEBER die Tier wechselt (im Gegensatz zur Sub-Nav, die in-tier ist).
- Aktiver Eintrag (`is-active`): Tier-Color-Tint (`bg` + `text` der Tier-Familie),
  damit der aktuelle Tier sichtbar ist.
- `transition: background 120ms`.

Barrierefreiheit (Spec §A6 / WCAG 2.4.1):
- `<nav>` traegt `aria-label` (Default "Hauptnavigation", per
  `TopNavInput.aria_label` ueberschreibbar) — mehrere `<nav>` pro Seite
  (L1 Top-Nav + L3 Sub-Nav) muessen fuer Screenreader unterscheidbar sein.
- Der aktive Eintrag traegt zusaetzlich `aria-current="page"` — die
  Aktiv-Information ist damit nicht rein visuell.

CSS-Strategie wie kpi_card / wetter_strip: Token-Werte via CSS Custom
Properties, `render_top_nav_css()` liefert Regeln fuer alle 4 Tiers.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import TopNavInput, WebTier

_TIERS: tuple[WebTier, ...] = (
    WebTier.BIBLIOTHEK,
    WebTier.ATELIER,
    WebTier.KABINETT,
    WebTier.START,
)


def render_top_nav_html(input: TopNavInput, *, inline_css: bool = False) -> str:
    """Top-Nav als HTML-Snippet (<nav> mit <a>-Pills).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_top_nav_css()}</style>")

    aria_label = escape(input.aria_label, quote=True)
    parts.append(f'<nav class="mn-top-nav" aria-label="{aria_label}">')
    for item in input.items:
        classes = ["mn-top-nav__item", f"mn-top-nav__item--{item.tier.value}"]
        aria_current = ""
        if item.active:
            classes.append("is-active")
            aria_current = ' aria-current="page"'
        href = escape(item.href, quote=True)
        label = escape(item.label)
        parts.append(
            f'<a class="{" ".join(classes)}" href="{href}"{aria_current}>{label}</a>'
        )
    parts.append("</nav>")
    return "".join(parts)


def render_top_nav_css() -> str:
    """Komponenten-CSS — Layout + 4 Tier-Aktiv-Modifier, Token-Werte via
    CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-tier-bibliothek-bg)` etc. greift.
    """
    rules = [
        """
.mn-top-nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  background: var(--color-dark-surface, #14141a);
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
}
.mn-top-nav__item {
  display: inline-block;
  padding: 0.3125rem 0.75rem;
  border-radius: var(--radius-round, 9999px);
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
  color: var(--color-dark-text, #f5f5f7);
  background: transparent;
  transition: background 120ms;
}
.mn-top-nav__item:hover {
  background: rgba(255, 255, 255, 0.08);
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        rules.append(
            f".mn-top-nav__item--{t}.is-active {{\n"
            f"  background: var(--color-tier-{t}-bg, #f0fdf4);\n"
            f"  color: var(--color-tier-{t}-text, #166534);\n"
            f"}}"
        )
    return "\n".join(rules)
