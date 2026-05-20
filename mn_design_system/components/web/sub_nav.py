"""Web-Renderer Sub-Nav — HTML + CSS, UX-Welle v0.2.

Konsumiert SubNavInput aus `_patterns.contracts`. L3 der 3-Layer-Affordance
(Spec §A5/A6): Auswahl-Navigation INNERHALB eines Tiers. Alle Tabs teilen den
Tier-Kontext der Sub-Nav.

CSS-Verhalten (Spec §A5/A6):
- Inaktiver Tab: nur Text, transparenter Hintergrund.
- Hover inaktiv: `var(--color-tier-<tier>-bg-soft)` — bg-soft-Token, zarter als
  Aktiv-bg, kein color-mix im Konsumenten (Gemini-Gate Punkt 1).
- Aktiver Tab (`is-active`): `bg` + `text` des Tiers, dauerhafter Chip-Look.
- `transition: background 120ms`.
- Sub-Nav-Background bleibt weiss (Barrierefreiheit, Spec §A6).

CSS-Strategie wie kpi_card / wetter_strip: Token-Werte via CSS Custom
Properties, `render_sub_nav_css()` liefert Regeln fuer alle 4 Tiers.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import SubNavInput, WebTier

_TIERS: tuple[WebTier, ...] = (
    WebTier.BIBLIOTHEK,
    WebTier.ATELIER,
    WebTier.KABINETT,
    WebTier.START,
)


def render_sub_nav_html(input: SubNavInput, *, inline_css: bool = False) -> str:
    """Sub-Nav als HTML-Snippet (<nav> mit <a>-Tabs).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_sub_nav_css()}</style>")

    parts.append(f'<nav class="mn-sub-nav mn-sub-nav--{input.tier.value}">')
    for tab in input.tabs:
        classes = ["mn-sub-nav__tab"]
        if tab.active:
            classes.append("is-active")
        href = escape(tab.href, quote=True)
        label = escape(tab.label)
        parts.append(f'<a class="{" ".join(classes)}" href="{href}">{label}</a>')
    parts.append("</nav>")
    return "".join(parts)


def render_sub_nav_css() -> str:
    """Komponenten-CSS — Layout + 4 Tier-Modifier, Token-Werte via Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-tier-bibliothek-bg-soft)` etc. greift.
    """
    rules = [
        """
.mn-sub-nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 1rem;
  background: var(--color-light-surface, #ffffff);
  border-bottom: 1px solid var(--color-light-border, #cbd5e1);
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
}
.mn-sub-nav__tab {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-subtle, 2px);
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
  color: var(--color-light-text, #1e1b4b);
  background: transparent;
  transition: background 120ms;
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        rules.append(
            f".mn-sub-nav--{t} .mn-sub-nav__tab:hover {{\n"
            f"  background: var(--color-tier-{t}-bg-soft, #f7fef9);\n"
            f"}}"
        )
        rules.append(
            f".mn-sub-nav--{t} .mn-sub-nav__tab.is-active {{\n"
            f"  background: var(--color-tier-{t}-bg, #f0fdf4);\n"
            f"  color: var(--color-tier-{t}-text, #166534);\n"
            f"}}"
        )
    return "\n".join(rules)
