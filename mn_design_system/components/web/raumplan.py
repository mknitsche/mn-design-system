"""Web-Renderer Raumplan — HTML + CSS, 0.24.0 (Welle 1 „Rahmen und Foyer“).

Konsumiert RaumplanInput aus `_patterns.contracts`. Der Raumplan ist die Handy-Form der
Raumleiste: alle Raeume mit Zwecksatz und ihren Reitern als Links.

Ohne Skript bedienbar, mit Rueckfall:
- Das HTML ist ein `<section id="raumplan" popover>`; der Raum-Schalter des kompakten Kopfes
  (`masthead`) oeffnet es per `popovertarget`.
- NUR wenn der Browser `:popover-open` kennt (`@supports selector(:popover-open)`), wird es ein
  Blatt von unten. Sonst bleibt es ein sichtbarer Abschnitt „Alle Raeume“ (der Schalter ist dann
  ein Link auf `#raumplan`); `display: block` gilt dort ausdruecklich, damit eine UA-Regel fuer
  `[popover]` den Abschnitt nicht verbirgt. In keinem Browser wird ein Raum unerreichbar.

CSS-Strategie: nur var(--…) mit Rueckfall, keine Literalfarbe, keine rohen Masse.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import RaumplanInput, RaumplanRaum


def _links(reiter: list[tuple[str, str]]) -> str:
    return "".join(
        f'<li><a href="{escape(href, quote=True)}">{escape(label)}</a></li>'
        for label, href in reiter
    )


def _raum_html(raum: RaumplanRaum) -> str:
    teile = [
        f'<li data-bereich="{escape(raum.slug, quote=True)}" class="mn-raumplan__raum">',
        (
            f'<a class="mn-raumplan__raum-link" href="{escape(raum.href, quote=True)}">'
            f"{escape(raum.label)}</a>"
        ),
        f'<p class="mn-raumplan__zweck">{escape(raum.zweck)}</p>',
    ]
    if raum.reiter:
        teile.append(f'<ul class="mn-raumplan__reiter">{_links(raum.reiter)}</ul>')
    for name, reiter in raum.gruppen or []:
        teile.append(f'<p class="mn-raumplan__gruppe">{escape(name)}</p>')
        teile.append(f'<ul class="mn-raumplan__reiter">{_links(reiter)}</ul>')
    teile.append("</li>")
    return "".join(teile)


def render_raumplan_html(input: RaumplanInput, *, inline_css: bool = False) -> str:
    """Raumplan als `<section id="raumplan" popover>` mit je einem `<li data-bereich=…>` je Raum."""
    html = (
        '<section id="raumplan" class="mn-raumplan" popover '
        'aria-labelledby="raumplan-titel">'
        '<div class="mn-raumplan__kopf">'
        f'<h2 id="raumplan-titel" class="mn-raumplan__titel">{escape(input.titel)}</h2>'
        '<button type="button" class="mn-raumplan__schliessen" '
        'popovertarget="raumplan" popovertargetaction="hide">Schließen</button>'
        "</div>"
        f'<ul class="mn-raumplan__raeume">{"".join(_raum_html(r) for r in input.raeume)}</ul>'
        "</section>"
    )
    if inline_css:
        return f"<style>{render_raumplan_css()}</style>{html}"
    return html


def render_raumplan_css() -> str:
    """Komponenten-CSS — sichtbarer Abschnitt als Standard, Blatt nur unter `@supports`."""
    return """
.mn-raumplan {
  display: block;
  box-sizing: border-box;
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text, #1e1b4b);
  background: var(--color-light-surface, #ffffff);
  padding: var(--space-4, 16px) var(--web-layout-page-inset, 44px);
}
.mn-raumplan__kopf {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3, 12px);
}
.mn-raumplan__schliessen {
  display: none;
}
.mn-raumplan__titel {
  margin: 0;
  font-size: var(--web-text-h3, 21px);
}
.mn-raumplan__raeume,
.mn-raumplan__reiter {
  margin: 0;
  padding: 0;
  list-style: none;
}
.mn-raumplan__raum {
  padding-block: var(--space-3, 12px);
  border-bottom: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
}
.mn-raumplan__raum-link {
  display: inline-flex;
  align-items: center;
  min-height: var(--web-touch-target, 44px);
  font-weight: 600;
  color: var(--color-light-text, #1e1b4b);
  text-decoration: none;
}
.mn-raumplan__zweck {
  margin: 0;
  color: var(--color-light-text-muted, #6b7280);
}
.mn-raumplan__gruppe {
  margin: var(--space-2, 8px) 0 0;
  font-size: var(--web-text-caption, 12px);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-raumplan__reiter {
  display: flex;
  flex-wrap: wrap;
}
.mn-raumplan__reiter a {
  display: inline-flex;
  align-items: center;
  min-height: var(--web-touch-target, 44px);
  padding-inline: var(--space-3, 12px);
  color: var(--color-light-accent, #4F46E5);
  text-decoration: none;
}
.mn-raumplan a:hover {
  text-decoration: underline;
}
.mn-raumplan a:focus-visible,
.mn-raumplan__schliessen:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}
@supports not selector(:popover-open) {
  .mn-raumplan {
    display: block;
  }
}
@supports selector(:popover-open) {
  .mn-raumplan {
    position: fixed;
    inset: auto 0 0 0;
    margin: 0;
    width: auto;
    max-height: calc(100% - var(--web-touch-target, 44px));
    overflow-y: auto;
    border: 0;
    border-top: var(--web-stroke-line-strong, 2px) solid var(--web-color-separator, #b4bcc8);
    border-radius: var(--radius-subtle, 2px) var(--radius-subtle, 2px) 0 0;
    padding-inline: var(--web-layout-page-inset, 16px);
  }
  .mn-raumplan:not(:popover-open) {
    display: none;
  }
  .mn-raumplan::backdrop {
    background: var(--color-dark-surface, #14141a);
    opacity: 0.5;
  }
  .mn-raumplan__schliessen {
    display: inline-flex;
    align-items: center;
    min-height: var(--web-touch-target, 44px);
    padding-inline: var(--space-3, 12px);
    font: inherit;
    color: var(--color-light-text, #1e1b4b);
    background: transparent;
    border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
    border-radius: var(--radius-subtle, 2px);
  }
}
""".strip()
