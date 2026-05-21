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
