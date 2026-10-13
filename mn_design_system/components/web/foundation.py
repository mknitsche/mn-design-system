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

from pathlib import Path

from mn_design_system.fonts import FONT_DIR
from mn_design_system.tokens import get

#: Die Web-Schriften des Design-Systems (v0.15.0): (Familie, Gewicht, Stil, Datei).
#: Bis 0.14.2 lagen die woff2-Dateien und diese Liste beim Konsumenten — ein Schriftwechsel
#: im Design-System zog im Web nicht nach, und Geist hatte dort keinen kursiven Schnitt
#: (der Browser schraegte kuenstlich an). Source Serif 4 wird von Google nur als Variable
#: Font ausgeliefert: eine Datei deckt den Gewichtsbereich ab.
WEB_SCHRIFTEN: tuple[tuple[str, str, str, str], ...] = (
    ("Geist", "300", "normal", "Geist-Light.woff2"),
    ("Geist", "400", "normal", "Geist-Regular.woff2"),
    ("Geist", "500", "normal", "Geist-Medium.woff2"),
    ("Geist", "700", "normal", "Geist-Bold.woff2"),
    ("Geist", "400", "italic", "Geist-Italic.woff2"),
    ("Geist", "500", "italic", "Geist-MediumItalic.woff2"),
    ("Geist", "700", "italic", "Geist-BoldItalic.woff2"),
    ("Source Serif 4", "400 600", "italic", "SourceSerif4-Italic.woff2"),
)


def web_font_dir() -> Path:
    """Verzeichnis der woff2-Dateien im installierten Paket — der Konsument kopiert von hier."""
    return FONT_DIR / "web"


def render_font_face(url_prefix: str) -> str:
    """@font-face-Bloecke fuer alle Web-Schriften; ``url_prefix`` ist der Auslieferpfad
    des Konsumenten (z. B. ``"/assets/fonts/"``). ``font-display: swap`` verhindert FOIT."""
    praefix = (
        url_prefix if not url_prefix or url_prefix.endswith("/") else url_prefix + "/"
    )
    return "\n".join(
        "@font-face {\n"
        f'  font-family: "{familie}";\n'
        f"  font-weight: {gewicht};\n"
        f"  font-style: {stil};\n"
        "  font-display: swap;\n"
        f'  src: url("{praefix}{datei}") format("woff2");\n'
        "}"
        for familie, gewicht, stil, datei in WEB_SCHRIFTEN
    )


#: Die Schluessel von :func:`css_font_stack` — zugleich die Namen der Tokens
#: ``web.font.<art>`` (Familie) und ``web.font.stack.<art>`` (Rueckfallkette).
_CSS_FONT_ARTEN: tuple[str, ...] = ("sans", "serif-editorial", "mono")


def css_font_stack(art: str) -> str:
    """Vollstaendiger CSS-Wert fuer ``font-family`` (v0.16.0): die Web-Familie in
    Anfuehrungszeichen, dahinter die Rueckfallkette — beides aus den Tokens.

    ``art`` ist ``"sans"``, ``"serif-editorial"`` oder ``"mono"``. Beispiel::

        css_font_stack("mono")
        # '"JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace'

    Die Anfuehrungszeichen sind noetig: ``--web-font-*`` gibt die Familie ohne sie aus,
    und ein Name mit Ziffer („Source Serif 4“) ist ungequotet kein gueltiger CSS-Bezeichner
    (CSS Fonts, ``family-name``). Ein Konsument setzt diesen Wert statt eines eigenen
    Literals (``font-family: Georgia, serif`` und aehnlich).

    Raises:
        KeyError: ``art`` ist keine der drei Arten (kein stilles Fallback).
    """
    if art not in _CSS_FONT_ARTEN:
        raise KeyError(
            f"Unbekannte Schriftart {art!r} (erlaubt: {list(_CSS_FONT_ARTEN)})"
        )
    return f'"{get(f"web.font.{art}")}", {get(f"web.font.stack.{art}")}'


def render_foundation_css() -> str:
    """Globale Responsive-Overrides der Web-Foundation-Tokens.

    - Tablet (<= bp-tablet): Seiten-Einzug 32px.
    - Mobil (<= bp-mobile): Seiten-Einzug 16px, Display-Stufen display/h1/h2/h3 eine
      Stufe kleiner. display wird zum Desktop-Wert von h1 (aus dem Token, kein Literal).
      Die spaetere Regel (mobil) gewinnt im Kaskaden-Konflikt.
    - Lese-Anker (body/ui/caption/lead) bleiben statisch — sie wandern nie.
    """
    bp_mobile = get("web.layout.bp-mobile")
    bp_tablet = get("web.layout.bp-tablet")
    display_mobil = get("web.text.h1")
    return f"""
@media (max-width: {bp_tablet}) {{
  :root {{ --web-layout-page-inset: 32px; }}
}}
@media (max-width: {bp_mobile}) {{
  :root {{
    --web-layout-page-inset: 16px;
    --web-text-display: {display_mobil};
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


def media_max_width_below(token: str) -> str:
    """Media-Query-Bedingung "knapp unter dem Breakpoint <token>".

    `render_foundation_css()` schaltet inklusiv (`max-width: 640px` gilt AUCH
    bei genau 640px). Komponenten, die "unter bp-mobile/bp-tablet" reagieren
    und ab dem Breakpoint unveraendert bleiben sollen (>= bp-tablet = Desktop),
    brauchen die strikte Form — sonst wuerde z.B. ein iPad im Querformat bei
    genau 1024px schon als Tablet gelten. 0,02px ist die uebliche Schrittweite
    unterhalb eines Pixels (kein Viewport liegt dazwischen).
    """
    px = float(get(token).removesuffix("px"))
    return f"max-width: {px - 0.02:g}px"
