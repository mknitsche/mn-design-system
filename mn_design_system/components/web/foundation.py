"""Web-Foundation CSS — globale Responsive-Overrides.

Style Dictionary emittiert einen flachen :root-Block (tokens.css) und kann
keine Media-Queries erzeugen. Diese Funktion liefert die responsive Schicht:
sie ueberschreibt die Foundation-Custom-Properties an den Breakpoints
web.layout.bp-mobile / bp-tablet (Design §9).

Der Konsument bindet render_foundation_css() einmal global ein — danach
reagieren ALLE Komponenten, die var(--web-layout-page-inset) / var(--web-text-h1)
etc. nutzen, automatisch responsiv. Eine Override-Stelle, kein Drift.
"""

from __future__ import annotations

from mn_design_system.tokens import get


def render_foundation_css() -> str:
    """Globale Responsive-Overrides der Web-Foundation-Tokens.

    - Tablet (<= bp-tablet): Seiten-Einzug 32px.
    - Mobil (<= bp-mobile): Seiten-Einzug 16px, Display-Stufen h1/h2/h3 eine
      Stufe kleiner. Die spaetere Regel (mobil) gewinnt im Kaskaden-Konflikt.
    - Lese-Anker (body/ui/caption/lead) bleiben statisch — sie wandern nie.
    """
    bp_mobile = get("web.layout.bp-mobile")
    bp_tablet = get("web.layout.bp-tablet")
    return f"""
@media (max-width: {bp_tablet}) {{
  :root {{ --web-layout-page-inset: 32px; }}
}}
@media (max-width: {bp_mobile}) {{
  :root {{
    --web-layout-page-inset: 16px;
    --web-text-h1: 27px;
    --web-text-h2: 24px;
    --web-text-h3: 21px;
  }}
}}
""".strip()


def render_initiale_css() -> str:
    """CSS fuer die zwei Initiale-Spielformen (Design §4 / §15.3).

    .mn-initiale       — Drop-Cap, 2 Zeilen hoch, Source Serif Italic.
                         initial-letter mit @supports-Fallback auf float.
    .mn-initiale-wort  — Wort-Initiale: erstes Wort in Source Serif Italic
                         1,3x, auf der Grundlinie stehend (kein Drop-Cap).

    Einsatz nur auf besonderen / textlastigen Seiten. Der Konsument kapselt
    den Eroeffnungs-Buchstaben bzw. das erste Wort in das jeweilige <span>.
    """
    return """
.mn-initiale {
  font-family: var(--web-font-serif-editorial, "Source Serif 4"), Georgia, serif;
  font-style: italic;
  font-weight: 600;
  color: var(--color-light-h1, #312e81);
}
@supports (initial-letter: 2) {
  .mn-initiale {
    -webkit-initial-letter: 2;
    initial-letter: 2;
    margin-right: var(--space-2, 8px);
  }
}
@supports not (initial-letter: 2) {
  .mn-initiale {
    float: left;
    font-size: 3.1em;
    line-height: 0.82;
    margin: 0.04em var(--space-2, 8px) 0 0;
  }
}
.mn-initiale-wort {
  font-family: var(--web-font-serif-editorial, "Source Serif 4"), Georgia, serif;
  font-style: italic;
  font-weight: 400;
  font-size: 1.3em;
  color: var(--color-light-h1, #312e81);
}
""".strip()
