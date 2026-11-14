"""Web-Renderer Masthead — HTML + CSS, Web-Foundation (Design §10).

Konsumiert MastheadInput aus `_patterns.contracts`. Editorialer Kopf von
mkn-desk.com: ein dunkler Block mit zwei Reihen — Reihe 1 Identitaet (Emblem
+ Wortmarke + Editions-Datum), Reihe 2 Tier-Navigation (Pills links,
Kontext-Chip rechts) — getrennt durch eine 2px-Linie. Loest top_nav +
brand_bar ab.

Das helle Lokal-Band (reine Sub-Navigation) ist NICHT Teil dieser
Komponente — es ist die sub_nav-Komponente, die der Konsument darunter
rendert.

Alle Masse, Schriftgroessen, Linien und der Fokus-Ring kommen aus
Foundation-Tokens (var(--web-*) / var(--space-*) / var(--radius-*)).
Kein roher rem-/px-Wert ausser der Token-Kette (Design §7 Box-Mitwachs).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import MastheadInput, WebTier
from mn_design_system.tokens import get

_TIERS: tuple[WebTier, ...] = (
    WebTier.BIBLIOTHEK,
    WebTier.ATELIER,
    WebTier.KABINETT,
    WebTier.START,
    WebTier.OBSERVATORIUM,
    WebTier.MAGAZIN,
    WebTier.ARCHIV,
)

# var()-Fallback je Tier (bg + text + hover-on-dark) — die ECHTEN
# color.tier.<tier>.* Werte aus tokens.py, damit Pills/Chips auch ohne
# geladene tokens.css ihren Tier-Ton behalten. Per
# test_tier_fallback_matches_real_tokens abgesichert.
_TIER_FALLBACK: dict[WebTier, tuple[str, str, str]] = {
    WebTier.BIBLIOTHEK: ("#f0fdf4", "#166534", "rgba(187,247,208,0.5)"),
    WebTier.ATELIER: ("#fffbeb", "#92400e", "rgba(253,230,138,0.5)"),
    WebTier.KABINETT: ("#fef2f2", "#991b1b", "rgba(254,202,202,0.5)"),
    WebTier.START: ("#f0fdf4", "#166534", "rgba(187,247,208,0.5)"),
    WebTier.OBSERVATORIUM: ("#fffbeb", "#92400e", "rgba(253,230,138,0.5)"),
    WebTier.MAGAZIN: ("#f5f5f5", "#374151", "rgba(229,231,235,0.5)"),
    WebTier.ARCHIV: ("#f5f5f5", "#374151", "rgba(229,231,235,0.5)"),
}


def render_masthead_html(input: MastheadInput, *, inline_css: bool = False) -> str:
    """Masthead als HTML-Snippet (<header> mit Identitaets- und Tier-Reihe).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_masthead_css()}</style>")

    kompakt = input.form == "kompakt"
    parts.append(
        '<header class="mn-masthead mn-masthead--kompakt">'
        if kompakt
        else '<header class="mn-masthead">'
    )

    # Reihe 1 — Identitaet
    emblem = input.emblem
    parts.append('<div class="mn-masthead__identity">')
    parts.append('<div class="mn-masthead__inner mn-masthead__identity-inner">')
    parts.append(
        f'<a class="mn-masthead__emblem" href="{escape(emblem.href, quote=True)}">'
        f'<img src="{escape(emblem.src, quote=True)}" alt="{escape(emblem.alt)}">'
        f"</a>"
    )
    parts.append('<div class="mn-masthead__brand">')
    parts.append(f'<span class="mn-masthead__wordmark">{escape(input.wordmark)}</span>')
    if input.edition_date is not None:
        parts.append(
            f'<span class="mn-masthead__edition">{escape(input.edition_date)}</span>'
        )
    parts.append("</div>")  # __brand
    parts.append("</div>")  # __identity-inner
    parts.append("</div>")  # __identity

    # Reihe 2 — Tier-Navigation
    parts.append(
        f'<nav class="mn-masthead__tiers" '
        f'aria-label="{escape(input.aria_label, quote=True)}">'
    )
    parts.append('<div class="mn-masthead__inner mn-masthead__tiers-inner">')
    parts.append('<div class="mn-masthead__pills">')
    for idx, item in enumerate(input.tier_items):
        classes = ["mn-masthead__pill", f"mn-masthead__pill--{item.tier.value}"]
        if kompakt and idx >= input.blicke:
            classes.append("mn-masthead__pill--raum")
        aria_current = ""
        if item.active:
            classes.append("is-active")
            aria_current = ' aria-current="page"'
        parts.append(
            f'<a class="{" ".join(classes)}" '
            f'href="{escape(item.href, quote=True)}"{aria_current}>'
            f"{escape(item.label)}</a>"
        )
        if (
            kompakt
            and 0 < input.blicke < len(input.tier_items)
            and idx + 1 == input.blicke
        ):
            parts.append(
                '<span class="mn-masthead__trenner" aria-hidden="true"></span>'
            )
    if kompakt and input.raum_schalter is not None:
        parts.append(_raum_schalter_html(input.raum_schalter))
    parts.append("</div>")  # __pills

    parts.append('<div class="mn-masthead__context">')
    if input.context_chip is not None:
        chip = input.context_chip
        parts.append(
            f'<span class="mn-masthead__chip mn-masthead__chip--{chip.tier.value}">'
            f"{escape(chip.label)}</span>"
        )
    if input.user_chip_id is not None:
        parts.append(
            f'<span id="{escape(input.user_chip_id, quote=True)}" '
            f'class="mn-masthead__chip mn-masthead__chip--loading">'
            f"{escape(input.user_chip_label)}</span>"
        )
    parts.append("</div>")  # __context
    parts.append("</div>")  # __tiers-inner
    parts.append("</nav>")  # __tiers

    parts.append("</header>")
    return "".join(parts)


def _raum_schalter_html(label: str) -> str:
    """Der Raum-Schalter steht doppelt: Knopf fuer das Raumplan-Blatt (`popovertarget`) und ein
    Rueckfall-Link auf `#raumplan`; das CSS zeigt genau einen von beiden."""
    inhalt = (
        f'<span class="mn-masthead__raum-name">{escape(label)}</span>'
        '<span class="mn-masthead__raum-pfeil" aria-hidden="true">▾</span>'
    )
    return (
        '<button type="button" class="mn-masthead__raum" popovertarget="raumplan" '
        f'aria-controls="raumplan">{inhalt}</button>'
        f'<a class="mn-masthead__raum-link" href="#raumplan">{inhalt}</a>'
    )


def render_masthead_css(*, kompakt: bool = False) -> str:
    """Komponenten-CSS — Layout + 6 Tier-Modifier, Token-Werte via Custom
    Properties. Konsument bindet `dist/css/tokens.css` ein.

    ``kompakt=True`` (0.24.0) haengt die Regeln der kompakten Form an; ohne das Argument
    ist die Ausgabe byte-gleich zu 0.23.0.
    """
    rules = [
        """
.mn-masthead {
  background: var(--color-dark-surface, #14141a);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-masthead__inner {
  max-width: var(--web-layout-content-width, 1024px);
  margin-inline: auto;
  padding-inline: var(--web-layout-page-inset, 44px);
}
.mn-masthead__identity {
  border-bottom: var(--web-stroke-line-strong, 2px) solid
    var(--web-color-separator-on-dark, rgba(255, 255, 255, 0.16));
}
.mn-masthead__identity-inner {
  display: flex;
  align-items: center;
  gap: var(--space-5, 20px);
  padding-block: var(--space-5, 20px);
}
.mn-masthead__emblem {
  display: inline-flex;
  align-items: center;
  padding: var(--space-2, 8px);
  border-radius: var(--radius-subtle, 2px);
  background: var(--color-light-surface, #ffffff);
}
.mn-masthead__emblem img {
  display: block;
  height: 2rem;
  width: auto;
}
.mn-masthead__emblem:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
.mn-masthead__brand {
  display: flex;
  flex-direction: column;
  gap: var(--space-1, 4px);
}
.mn-masthead__wordmark {
  font-family: var(--web-font-serif-editorial, "Source Serif 4"), Georgia, serif;
  font-style: italic;
  font-size: var(--web-text-lead, 19px);
  line-height: var(--web-leading-lead, 1.55);
  color: var(--color-dark-text, #f5f5f7);
}
.mn-masthead__edition {
  font-size: var(--web-text-caption, 12px);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-dark-text, #f5f5f7);
  opacity: 0.62;
}
.mn-masthead__tiers-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3, 12px);
  padding-block: var(--space-2, 8px);
}
.mn-masthead__pills {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-1, 4px);
}
.mn-masthead__pill {
  display: inline-block;
  padding: var(--space-1, 4px) var(--space-3, 12px);
  border-radius: var(--radius-round, 9999px);
  font-size: var(--web-text-ui, 14px);
  font-weight: 500;
  text-decoration: none;
  color: var(--color-dark-text, #f5f5f7);
  background: transparent;
  transition: background 120ms;
}
.mn-masthead__pill:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
.mn-masthead__context {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2, 8px);
}
.mn-masthead__chip {
  display: inline-block;
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border-radius: var(--radius-subtle, 2px);
  font-size: var(--web-text-caption, 12px);
  font-weight: 600;
  line-height: var(--web-leading-caption, 1.4);
}
.mn-masthead__chip--loading {
  color: var(--color-dark-text, #f5f5f7);
  opacity: 0.6;
  font-style: italic;
}
""".strip()
    ]
    for tier in _TIERS:
        t = tier.value
        fb_bg, fb_text, fb_hover = _TIER_FALLBACK[tier]
        rules.append(
            f".mn-masthead__pill--{t}:not(.is-active):hover {{\n"
            f"  background: var(--color-tier-{t}-hover-on-dark, {fb_hover});\n"
            f"  color: var(--color-dark-text, #f5f5f7);\n"
            f"  text-decoration: none;\n"
            f"}}"
        )
        rules.append(
            f".mn-masthead__pill--{t}.is-active {{\n"
            f"  background: var(--color-tier-{t}-bg, {fb_bg});\n"
            f"  color: var(--color-tier-{t}-text, {fb_text});\n"
            f"}}"
        )
        rules.append(
            f".mn-masthead__chip--{t} {{\n"
            f"  background: var(--color-tier-{t}-bg, {fb_bg});\n"
            f"  color: var(--color-tier-{t}-text, {fb_text});\n"
            f"}}"
        )
    if kompakt:
        rules.append(_kompakt_css())
    return "\n".join(rules)


def _kompakt_css() -> str:
    """Regeln der kompakten Form (0.24.0): nach dem Basis-CSS. Der Trenner steht ueberall; am
    Handy (bis `web.layout.bp-mobile`) ist es EINE Zeile ohne Markenzeile und Raum-Pillen."""
    bp_mobile = get("web.layout.bp-mobile")
    return f"""
.mn-masthead__trenner {{
  align-self: stretch;
  width: var(--web-stroke-line, 1px);
  margin-block: var(--space-1, 4px);
  background: var(--web-color-separator-on-dark, rgba(255, 255, 255, 0.16));
}}
.mn-masthead__raum,
.mn-masthead__raum-link {{
  display: none;
}}
@media (max-width: {bp_mobile}) {{
  .mn-masthead--kompakt {{
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding-inline: var(--web-layout-page-inset, 16px);
  }}
  .mn-masthead--kompakt .mn-masthead__inner {{
    max-width: none;
    margin-inline: 0;
    padding-inline: 0;
  }}
  .mn-masthead--kompakt .mn-masthead__identity {{
    flex: none;
    border-bottom: 0;
  }}
  .mn-masthead--kompakt .mn-masthead__identity-inner {{
    padding-block: 0;
  }}
  .mn-masthead--kompakt .mn-masthead__brand {{
    display: none;
  }}
  .mn-masthead--kompakt .mn-masthead__emblem {{
    padding: var(--space-1, 4px);
  }}
  .mn-masthead--kompakt .mn-masthead__tiers {{
    flex: 1 1 auto;
    min-width: 0;
  }}
  .mn-masthead--kompakt .mn-masthead__tiers-inner {{
    flex-wrap: nowrap;
    gap: var(--space-1, 4px);
    padding-block: 0;
  }}
  .mn-masthead--kompakt .mn-masthead__pills {{
    flex-wrap: nowrap;
    min-width: 0;
  }}
  .mn-masthead--kompakt .mn-masthead__pill {{
    box-sizing: border-box;
    display: inline-flex;
    flex: none;
    align-items: center;
    min-height: var(--web-touch-target, 44px);
    padding-inline: var(--space-2, 8px);
    white-space: nowrap;
  }}
  .mn-masthead--kompakt .mn-masthead__pill--raum {{
    display: none;
  }}
  .mn-masthead--kompakt .mn-masthead__raum-link,
  .mn-masthead--kompakt .mn-masthead__raum {{
    align-items: center;
    min-height: var(--web-touch-target, 44px);
    padding: 0 var(--space-2, 8px);
    font: inherit;
    font-size: var(--web-text-ui, 14px);
    font-weight: 500;
    white-space: nowrap;
    min-width: 0;
    gap: var(--space-1, 4px);
    color: var(--color-dark-text, #f5f5f7);
    text-decoration: none;
    background: transparent;
    border: 0;
    border-radius: var(--radius-round, 9999px);
  }}
  .mn-masthead--kompakt .mn-masthead__raum-link {{
    display: inline-flex;
  }}
  .mn-masthead--kompakt .mn-masthead__raum-name {{
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .mn-masthead--kompakt .mn-masthead__raum-pfeil {{
    flex: none;
  }}
  .mn-masthead--kompakt .mn-masthead__raum:focus-visible,
  .mn-masthead--kompakt .mn-masthead__raum-link:focus-visible {{
    outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
    outline-offset: var(--space-1, 4px);
  }}
  .mn-masthead--kompakt .mn-masthead__context {{
    margin-inline-start: auto;
    flex: none;
  }}
}}
@supports selector(:popover-open) {{
  @media (max-width: {bp_mobile}) {{
    .mn-masthead--kompakt .mn-masthead__raum {{
      display: inline-flex;
    }}
    .mn-masthead--kompakt .mn-masthead__raum-link {{
      display: none;
    }}
  }}
}}""".strip()
