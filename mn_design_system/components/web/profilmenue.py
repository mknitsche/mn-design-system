"""Web-Renderer Profil-Menue — HTML + CSS, 0.24.0 (Welle 1, Plan T24).

Konsumiert ProfilMenueInput aus `_patterns.contracts`. Das Menue gehoert zum Profil-Knopf des
Kopfes (`MastheadInput.profil`): „Darstellung“ mit drei Knoepfen (Automatisch · Hell · Dunkel,
`data-schema-wahl`, `aria-pressed`) und der Link „Profil ansehen“. Bedient wird es vom
Schema-Skript (`render_schema_js`); die Wahl liegt nur im Browser.

Ohne Skript bedienbar, mit Rueckfall (wie der Raumplan):
- Das HTML ist ein `<div id="profilmenue" popover>`; der Profil-Knopf oeffnet es per
  `popovertarget`.
- NUR wenn der Browser `:popover-open` kennt (`@supports selector(:popover-open)`), wird es ein
  schwebendes Menue am Knopf. Sonst steht es als sichtbarer Abschnitt dort, wo der Konsument es
  platziert (am Seitenende), und der Knopf ist ein Link auf `#profilmenue`.

`render_profilmenue_css()` traegt auch die Regeln des Profil-Knopfes im Kopf und das Verbergen der
Chips am Handy (kompakte Form mit Profil): die Ausgabe von `render_masthead_css()` bleibt so
byte-gleich zu 0.23.0.
CSS-Strategie: nur var(--…) mit Rueckfall, keine Literalfarbe, keine rohen Masse.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import ProfilMenueInput
from mn_design_system.tokens import get

_WAHL = (("auto", "Automatisch"), ("hell", "Hell"), ("dunkel", "Dunkel"))


def render_profilmenue_html(
    input: ProfilMenueInput, *, inline_css: bool = False
) -> str:
    """Profil-Menue als `<div id="profilmenue" class="mn-profilmenue" popover>`."""
    knoepfe = "".join(
        f'<button type="button" class="mn-profilmenue__wahl" data-schema-wahl="{wert}" '
        f'aria-pressed="{"true" if wert == "auto" else "false"}">{label}</button>'
        for wert, label in _WAHL
    )
    html = (
        '<div id="profilmenue" class="mn-profilmenue" popover '
        'aria-labelledby="profilmenue-titel">'
        f'<p id="profilmenue-titel" class="mn-profilmenue__titel">{escape(input.titel)}</p>'
        f'<div class="mn-profilmenue__wahlen" role="group" '
        f'aria-labelledby="profilmenue-titel">{knoepfe}</div>'
        f'<a class="mn-profilmenue__link" href="{escape(input.profil_href, quote=True)}">'
        "Profil ansehen</a>"
        "</div>"
    )
    if inline_css:
        return f"<style>{render_profilmenue_css()}</style>{html}"
    return html


def render_profilmenue_css() -> str:
    """Komponenten-CSS — Menue, Profil-Knopf im Kopf, Chips am Handy verborgen."""
    bp_mobile = get("web.layout.bp-mobile")
    return f"""
.mn-masthead__profil,
.mn-masthead__profil-link {{
  box-sizing: border-box;
  align-items: center;
  justify-content: center;
  min-width: var(--web-touch-target, 44px);
  min-height: var(--web-touch-target, 44px);
  padding: 0;
  font: inherit;
  color: var(--color-dark-text, #f5f5f7);
  text-decoration: none;
  background: transparent;
  border: 0;
  border-radius: var(--radius-round, 9999px);
  cursor: pointer;
}}
.mn-masthead__profil {{
  display: none;
  anchor-name: --mn-profil;
}}
.mn-masthead__profil-link {{
  display: inline-flex;
  anchor-name: --mn-profil;
}}
.mn-masthead__profil:hover,
.mn-masthead__profil-link:hover {{
  background: var(--web-color-separator-on-dark, rgba(255, 255, 255, 0.16));
}}
.mn-masthead__profil:focus-visible,
.mn-masthead__profil-link:focus-visible {{
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}}
@media (max-width: {bp_mobile}) {{
  .mn-masthead--kompakt.mn-masthead--profil .mn-masthead__chip {{
    display: none;
  }}
}}
.mn-profilmenue {{
  display: block;
  box-sizing: border-box;
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text, #1e1b4b);
  background: var(--color-light-surface, #ffffff);
  padding: var(--space-4, 16px) var(--web-layout-page-inset, 44px);
}}
.mn-profilmenue__titel {{
  margin: 0 0 var(--space-2, 8px);
  font-size: var(--web-text-caption, 12px);
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-light-text-muted, #6b7280);
}}
.mn-profilmenue__wahlen {{
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2, 8px);
}}
.mn-profilmenue__wahl {{
  box-sizing: border-box;
  min-height: var(--web-touch-target, 44px);
  padding-inline: var(--space-3, 12px);
  font: inherit;
  color: var(--color-light-text, #1e1b4b);
  background: transparent;
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-round, 9999px);
  cursor: pointer;
}}
.mn-profilmenue__wahl[aria-pressed="true"] {{
  color: var(--color-light-surface, #ffffff);
  background: var(--color-light-accent, #4F46E5);
  border-color: var(--color-light-accent, #4F46E5);
}}
.mn-profilmenue__link {{
  display: inline-flex;
  align-items: center;
  min-height: var(--web-touch-target, 44px);
  margin-top: var(--space-2, 8px);
  color: var(--color-light-accent, #4F46E5);
  text-decoration: none;
}}
.mn-profilmenue__link:hover {{
  text-decoration: underline;
}}
.mn-profilmenue__wahl:focus-visible,
.mn-profilmenue__link:focus-visible {{
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}}
@supports selector(:popover-open) {{
  .mn-masthead__profil {{
    display: inline-flex;
  }}
  .mn-masthead__profil-link {{
    display: none;
  }}
  .mn-profilmenue {{
    position: fixed;
    inset: auto;
    top: calc(var(--web-touch-target, 44px) + var(--space-2, 8px));
    right: var(--web-layout-page-inset, 16px);
    margin: 0;
    padding: var(--space-4, 16px);
    max-width: calc(100% - 2 * var(--web-layout-page-inset, 16px));
    border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
    border-radius: var(--radius-card, 4px);
  }}
  .mn-profilmenue:not(:popover-open) {{
    display: none;
  }}
}}
@supports (top: anchor(bottom)) {{
  .mn-profilmenue {{
    position-anchor: --mn-profil;
    top: calc(anchor(bottom) + var(--space-1, 4px));
    right: anchor(right);
  }}
}}
""".strip()
