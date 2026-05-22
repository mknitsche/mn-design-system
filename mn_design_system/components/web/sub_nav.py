"""Web-Renderer Sub-Nav — HTML + CSS, UX-Welle v0.2.

Konsumiert SubNavInput aus `_patterns.contracts`. L3 der 3-Layer-Affordance
(Spec §A5/A6): Auswahl-Navigation INNERHALB eines Tiers. Alle Tabs teilen den
Tier-Kontext der Sub-Nav.

CSS-Verhalten (Spec §A5/A6, Hover-Revision cld1-S21):
- Inaktiver Tab: nur Text, transparenter Hintergrund.
- Hover inaktiv: `var(--color-tier-<tier>-border)` — ein klar sichtbarer
  Tier-Tint (analog zum Masthead-Tier-Hover); die Link-Unterstreichung des
  Konsumenten wird im Nav-Kontext unterdrueckt.
- Aktiver Tab (`is-active`): `bg` + `text` des Tiers, dauerhafter Chip-Look —
  das Aktiv-Signal traegt die Tier-Textfarbe, der Hover die Tier-Flaeche.
- `transition: background 120ms`.
- Sub-Nav-Background bleibt weiss (Barrierefreiheit, Spec §A6).

Barrierefreiheit (Spec §A6):
- `<nav>` traegt `aria-label` (Default "Bereichs-Navigation", per
  `SubNavInput.aria_label` ueberschreibbar) — mehrere `<nav>` pro Seite
  (L1 Top-Nav + L3 Sub-Nav) muessen fuer Screenreader unterscheidbar sein.
- Der aktive Tab traegt zusaetzlich `aria-current="page"` — die
  Aktiv-Information ist damit nicht rein visuell.

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

# var()-Fallback je Tier (bg + border + text) — die ECHTEN color.tier.<tier>.*
# Werte aus tokens.py, damit Hover/Aktiv-Tabs auch ohne geladene tokens.css
# ihren Tier-Ton behalten.
_TIER_FALLBACK: dict[WebTier, tuple[str, str, str]] = {
    WebTier.BIBLIOTHEK: ("#f0fdf4", "#bbf7d0", "#166534"),
    WebTier.ATELIER: ("#fffbeb", "#fde68a", "#92400e"),
    WebTier.KABINETT: ("#fef2f2", "#fecaca", "#991b1b"),
    WebTier.START: ("#f0fdf4", "#bbf7d0", "#166534"),
}


def render_sub_nav_html(input: SubNavInput, *, inline_css: bool = False) -> str:
    """Sub-Nav als HTML-Snippet (<nav> mit <a>-Tabs).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts = []
    if inline_css:
        parts.append(f"<style>{render_sub_nav_css()}</style>")

    aria_label = escape(input.aria_label, quote=True)
    parts.append(
        f'<nav class="mn-sub-nav mn-sub-nav--{input.tier.value}" '
        f'aria-label="{aria_label}">'
    )
    parts.append('<div class="mn-sub-nav__inner">')
    for tab in input.tabs:
        classes = ["mn-sub-nav__tab"]
        aria_current = ""
        if tab.active:
            classes.append("is-active")
            aria_current = ' aria-current="page"'
        href = escape(tab.href, quote=True)
        label = escape(tab.label)
        parts.append(
            f'<a class="{" ".join(classes)}" href="{href}"{aria_current}>{label}</a>'
        )
    parts.append("</div>")
    parts.append("</nav>")
    return "".join(parts)


def render_sub_nav_css() -> str:
    """Komponenten-CSS — Layout + 4 Tier-Modifier, Token-Werte via Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-tier-bibliothek-bg)` etc. greift.
    """
    rules = [
        """
.mn-sub-nav {
  background: var(--color-light-surface, #ffffff);
  border-bottom: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-sub-nav__inner {
  max-width: var(--web-layout-content-width, 1024px);
  margin-inline: auto;
  padding: var(--space-2, 8px) var(--web-layout-page-inset, 44px);
  display: flex;
  align-items: center;
  gap: var(--space-1, 4px);
}
.mn-sub-nav__tab {
  display: inline-block;
  padding: var(--space-1, 4px) var(--space-3, 12px);
  border-radius: var(--radius-subtle, 2px);
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  font-weight: 500;
  text-decoration: none;
  color: var(--color-light-text, #1e1b4b);
  background: transparent;
  transition: background 120ms;
}
.mn-sub-nav__tab:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        fb_bg, fb_border, fb_text = _TIER_FALLBACK[tier]
        rules.append(
            f".mn-sub-nav--{t} .mn-sub-nav__tab:not(.is-active):hover {{\n"
            f"  background: var(--color-tier-{t}-border, {fb_border});\n"
            f"  color: var(--color-light-text, #1e1b4b);\n"
            f"  text-decoration: none;\n"
            f"}}"
        )
        rules.append(
            f".mn-sub-nav--{t} .mn-sub-nav__tab.is-active {{\n"
            f"  background: var(--color-tier-{t}-bg, {fb_bg});\n"
            f"  color: var(--color-tier-{t}-text, {fb_text});\n"
            f"}}"
        )
    return "\n".join(rules)
