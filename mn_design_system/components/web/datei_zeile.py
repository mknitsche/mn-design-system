"""Web-Renderer Listenzeile fuer Ordner und Dateien — HTML + CSS, 0.20.0 (Magazin-Welle 0).

Konsumiert DateiZeileInput aus `_patterns.contracts`. Klassenvertrag: `mn-datei-liste` (ul),
`mn-datei-zeile` (li, `--ordner`), Elemente `__kennung`, `__vorschau`, `__name`, `__satz`,
`__etikett`, `__meta`, `__meta--groesse`, `__neu`, `__aktion`. Der Browser-Konsument baut
dieselben Klassen per DOM; dieser Renderer dient dem statischen Seitenbau (Archiv).

Aufbau: Gitter mit benannten Bereichen k (Kennung), n (Name), s (Satz), m (Datum), g (Groesse),
a (Aktion). Bis `web.layout.bp-mobile` zweizeilig (Name / Meta), die Groesse faellt weg
(sie haengt am Datum). Ordner: ganze Zeile ist der Link (gestreckter Name-Link), der Pfeil
steht im Aktionsfeld. Datei: Name ist der Link, `⋯` ist ein eigener Knopf darueber.

CSS-Strategie: nur var(--…) mit Rueckfall, keine Literalfarbe, keine feste Laenge.
"""

from __future__ import annotations

from collections.abc import Sequence
from html import escape

from mn_design_system.components._patterns.contracts import DateiZeileInput
from mn_design_system.tokens import get


def _e(text: str) -> str:
    return escape(text, quote=True)


def render_datei_zeile_html(z: DateiZeileInput, *, inline_css: bool = False) -> str:
    """Eine Zeile (`<li>`); mit inline_css=True geht ein <style>-Block voran."""
    ordner = z.art == "ordner"
    klasse = "mn-datei-zeile mn-datei-zeile--ordner" if ordner else "mn-datei-zeile"
    teile = [f'<li class="{klasse}">']
    if z.vorschau_src:
        teile.append(
            f'<img class="mn-datei-zeile__vorschau" src="{_e(z.vorschau_src)}" alt="" loading="lazy">'
        )
    elif z.kennung:
        teile.append(f'<span class="mn-datei-zeile__kennung">{_e(z.kennung)}</span>')
    teile.append(
        f'<a class="mn-datei-zeile__name" href="{_e(z.href)}">{_e(z.name)}</a>'
    )
    if z.neu:
        teile.append('<span class="mn-datei-zeile__neu">neu</span>')
    if z.satz or z.etikett:
        inhalt = []
        if z.satz:
            inhalt.append(_e(z.satz))
        if z.etikett:
            inhalt.append(
                f'<span class="mn-datei-zeile__etikett">{_e(z.etikett)}</span>'
            )
        teile.append(f'<span class="mn-datei-zeile__satz">{" ".join(inhalt)}</span>')
    if z.datum:
        teile.append(f'<span class="mn-datei-zeile__meta">{_e(z.datum)}</span>')
    # Groesse (Datei) bzw. Inhalt (Ordner) teilen sich die rechte Meta-Spalte
    rechts = z.inhalt if ordner else z.groesse
    if rechts:
        teile.append(
            f'<span class="mn-datei-zeile__meta mn-datei-zeile__meta--groesse">{_e(rechts)}</span>'
        )
    if ordner:
        teile.append('<span class="mn-datei-zeile__aktion" aria-hidden="true">›</span>')
    elif z.aktion_label:
        teile.append(
            f'<button type="button" class="mn-datei-zeile__aktion" aria-label="{_e(z.aktion_label)}">⋯</button>'
        )
    teile.append("</li>")
    html = "".join(teile)
    return f"<style>{render_datei_zeile_css()}</style>{html}" if inline_css else html


def render_datei_liste_html(
    zeilen: Sequence[DateiZeileInput], *, label: str, inline_css: bool = False
) -> str:
    """Die Liste (`<ul>`): Reihenfolge wie uebergeben (Ordner zuerst ist Sache des Konsumenten)."""
    html = (
        f'<ul class="mn-datei-liste" aria-label="{_e(label)}">'
        + "".join(render_datei_zeile_html(z) for z in zeilen)
        + "</ul>"
    )
    return f"<style>{render_datei_zeile_css()}</style>{html}" if inline_css else html


def render_datei_zeile_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties."""
    bp = get("web.layout.bp-mobile")
    return (
        """
.mn-datei-liste {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: var(--web-stroke-line, 1px) solid var(--color-light-border, #cbd5e1);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-datei-zeile {
  position: relative;
  display: grid;
  grid-template-columns: var(--web-touch-target, 44px) minmax(0, 1fr) auto auto var(--web-touch-target, 44px);
  grid-template-areas: "k n m g a" "k s m g a";
  column-gap: var(--space-4, 16px);
  align-items: center;
  min-height: var(--web-touch-target, 44px);
  padding: var(--space-2, 8px) 0;
  border-bottom: var(--web-stroke-line, 1px) solid var(--color-light-border, #cbd5e1);
}
.mn-datei-zeile__kennung,
.mn-datei-zeile__vorschau {
  grid-area: k;
  align-self: center;
}
.mn-datei-zeile__kennung {
  display: inline-block;
  justify-self: start;
  white-space: nowrap;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  font-weight: var(--font-weight-medium, 500);
  letter-spacing: var(--font-tracking-wide, 0.04em);
  text-transform: uppercase;
  color: var(--color-light-text-muted, #6b7280);
  border: var(--web-stroke-line, 1px) solid var(--color-light-border, #cbd5e1);
  border-radius: var(--radius-subtle, 2px);
  padding: 0 var(--space-1, 4px);
}
.mn-datei-zeile__vorschau {
  width: var(--space-10, 40px);
  height: var(--space-10, 40px);
  object-fit: cover;
  border-radius: var(--radius-subtle, 2px);
  background: var(--color-light-surface-subtle, #f6f6f6);
}
.mn-datei-zeile__name {
  grid-area: n;
  min-width: 0;
  overflow-wrap: anywhere;
  font-size: var(--web-text-body, 16px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text, #1e1b4b);
  text-decoration: none;
}
.mn-datei-zeile--ordner .mn-datei-zeile__name {
  font-weight: var(--font-weight-medium, 500);
}
.mn-datei-zeile--ordner .mn-datei-zeile__name::after {
  content: "";
  position: absolute;
  inset: 0;
}
.mn-datei-zeile__name:hover {
  color: var(--color-light-accent, #4F46E5);
  text-decoration: underline;
}
.mn-datei-zeile__name:focus-visible,
.mn-datei-zeile__aktion:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: var(--space-1, 4px);
}
.mn-datei-zeile__satz {
  grid-area: s;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-datei-zeile__etikett {
  font-size: var(--web-text-caption, 12px);
  font-weight: var(--font-weight-medium, 500);
  letter-spacing: var(--font-tracking-wide, 0.04em);
  text-transform: uppercase;
}
.mn-datei-zeile__meta {
  grid-area: m;
  text-align: right;
  font-size: var(--web-text-ui, 14px);
  line-height: var(--web-leading-ui, 1.35);
  color: var(--color-light-text-muted, #6b7280);
  font-variant-numeric: tabular-nums;
}
.mn-datei-zeile__meta--groesse {
  grid-area: g;
}
.mn-datei-zeile__neu {
  grid-area: n;
  justify-self: end;
  font-size: var(--web-text-caption, 12px);
  font-weight: var(--font-weight-medium, 500);
  letter-spacing: var(--font-tracking-wide, 0.04em);
  text-transform: uppercase;
  color: var(--color-light-accent, #4F46E5);
}
.mn-datei-zeile__aktion {
  grid-area: a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--web-touch-target, 44px);
  height: var(--web-touch-target, 44px);
  padding: 0;
  border: 0;
  background: transparent;
  font: inherit;
  color: var(--color-light-text-muted, #6b7280);
  position: relative;
}
button.mn-datei-zeile__aktion {
  cursor: pointer;
}
button.mn-datei-zeile__aktion:hover {
  background: var(--color-light-surface-subtle, #f6f6f6);
}
@media (max-width: %s) {
  .mn-datei-zeile {
    grid-template-columns: var(--web-touch-target, 44px) minmax(0, 1fr) var(--web-touch-target, 44px);
    grid-template-areas: "k n a" "k s a" "k m a";
    column-gap: var(--space-3, 12px);
  }
  .mn-datei-zeile__meta {
    text-align: left;
  }
  .mn-datei-zeile__meta--groesse {
    display: none;
  }
}
""".strip()
        % bp
    )
