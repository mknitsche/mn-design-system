"""Font-Registration fuer ReportLab.

Public-API:
    from mn_design_system.fonts import register_all_fonts, FONT_DIR
    register_all_fonts()  # einmal beim App-Start

Registriert alle TTF-Files unter mn_design_system/fonts/ beim ReportLab — und seit
v0.15.0 die SCHRIFTFAMILIEN dazu. ReportLab loest ``<b>``/``<i>`` in einem Paragraph
ueber die Familien-Zuordnung auf; ohne sie setzt es still den Grundschnitt. Bis 0.14.2
waren Fett und Kursiv deshalb in allen ReportLab-PDFs der Konsumenten unsichtbar.
Idempotent: mehrfache Aufrufe sind harmlos. ReportLab UEBERSCHREIBT einen schon
geladenen Namen NICHT: die Ersatznamen „Helvetica"/„Helvetica-Oblique" wirken nur, wenn
``register_all_fonts()`` vor der ersten ReportLab-Nutzung laeuft (sonst bleibt dort die
eingebaute Type-1-Helvetica). Darum: einmal beim App-Start.
"""

from __future__ import annotations

import logging
from importlib.resources import files
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_LOG = logging.getLogger(__name__)

# FONT_DIR liefert den absoluten Pfad zu den TTF-Files dieses Packages.
# Funktioniert mit pip install -e und mit Wheel-Install.
FONT_DIR: Path = Path(str(files("mn_design_system") / "fonts"))

# Mapping ReportLab-Name -> relativer Pfad zu mn_design_system/fonts/
# Bewusst minimaler Default-Set; Konsumenten koennen eigene registrieren.
_FONT_MAP: dict[str, str] = {
    "Geist": "geist/Geist-Regular.ttf",
    "Geist-Bold": "geist/Geist-Bold.ttf",
    "Geist-Medium": "geist/Geist-Medium.ttf",
    "Geist-Light": "geist/Geist-Light.ttf",
    # v0.15.0: echte Kursiv-Schnitte (Geist 1.800, SIL OFL — Lizenz in geist/OFL.txt).
    "Geist-Italic": "geist/Geist-Italic.ttf",
    "Geist-MediumItalic": "geist/Geist-MediumItalic.ttf",
    "Geist-BoldItalic": "geist/Geist-BoldItalic.ttf",
    "SourceSerif": "source-serif/SourceSerif4-Regular.ttf",
    "SourceSerif-Italic": "source-serif/SourceSerif4-Italic.ttf",
    "SourceSerif-Bold": "source-serif/SourceSerif4-Bold.ttf",
    "SourceSerif-BoldItalic": "source-serif/SourceSerif4-BoldItalic.ttf",
    # Token-Name font.family.italic-editorial (v0.15.0): die Tokens tragen den Dateinamen
    # (LaTeX/fontspec braucht ihn); ReportLab kannte nur den Kurznamen — wer den Token
    # nahm, bekam seit v0.5.0 einen ValueError beim Rendern.
    "SourceSerif4-Italic": "source-serif/SourceSerif4-Italic.ttf",
    # v0.16.0: Token font.family.italic-editorial-bold (der Schnitt, den <b> in der
    # Zitat-Kursive ergibt) — derselbe Fett-Kursiv-Schnitt wie SourceSerif-BoldItalic.
    "SourceSerif4-BoldItalic": "source-serif/SourceSerif4-BoldItalic.ttf",
    "SourceSans": "source-sans/SourceSans3-Regular.ttf",
    "SourceSans-Bold": "source-sans/SourceSans3-Bold.ttf",
    "SourceSans-Italic": "source-sans/SourceSans3-Italic.ttf",
    "SourceSans-BoldItalic": "source-sans/SourceSans3-BoldItalic.ttf",
    "JetBrainsMono": "jetbrains-mono/JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Bold": "jetbrains-mono/JetBrainsMono-Bold.ttf",
    "Phosphor": "phosphor/Phosphor.ttf",
    "Phosphor-Light": "phosphor/Phosphor-Light.ttf",
    "Phosphor-Bold": "phosphor/Phosphor-Bold.ttf",
    "Phosphor-Fill": "phosphor/Phosphor-Fill.ttf",
    "Phosphor-Duotone": "phosphor/Phosphor-Duotone.ttf",
    "Inter": "inter/Inter-Regular.ttf",
    "Inter-Bold": "inter/Inter-Bold.ttf",
    "Inter-Italic": "inter/Inter-Italic.ttf",
    "Inter-BoldItalic": "inter/Inter-BoldItalic.ttf",
    "NotoSans": "noto/NotoSans-Regular.ttf",
    "NotoSans-Bold": "noto/NotoSans-Bold.ttf",
    "NotoSans-Italic": "noto/NotoSans-Italic.ttf",
    "NotoSans-BoldItalic": "noto/NotoSans-BoldItalic.ttf",
    "NotoSansSymbols2": "noto/NotoSansSymbols2-Regular.ttf",
    "STIXTwo": "stix-two/STIXTwoText-Regular.ttf",
    "STIXTwo-Italic": "stix-two/STIXTwoText-Italic.ttf",
    "STIXTwo-Bold": "stix-two/STIXTwoText-Bold.ttf",
    # Aliase fuer helpers.font_with_fallback-Output (S249, macb-claude):
    # font_with_fallback wrappt Greek-Chars in <font name="STIXTwoText">...</font>,
    # daher muss der lange Name auch in pdfmetrics aufloesbar sein. Sonst
    # ValueError beim PDF-Render (Bug-Trail: claudeAI daily-engine 2026-05-10).
    "STIXTwoText": "stix-two/STIXTwoText-Regular.ttf",
    "STIXTwoText-Italic": "stix-two/STIXTwoText-Italic.ttf",
    "STIXTwoText-Bold": "stix-two/STIXTwoText-Bold.ttf",
    # Kein STIXTwoText-BoldItalic im Paket (bis 0.14.2 stand hier ein Eintrag auf eine
    # fehlende Datei, still uebersprungen); die Familie nimmt dafuer den Fettschnitt.
    # S249 (macb-claude) Greek-Glyph-Fix — finale Loesung:
    # STIXTwoText-Greek.ttf teilt sich den PostScript-Namen 'STIXTwoText-Regular'
    # mit der Latin-TTF (verifiziert via fontTools NameID 6) → ReportLab-Cache-
    # Kollision: erste registrierte Variante (= Latin ohne Greek) gewinnt, σ
    # wird als .notdef-BOX gerendert. STIXTwoMath hat eindeutigen PS-Name
    # 'STIXTwoMath', ist 4138 Glyphen vollstaendig (Greek + Math + Latin),
    # σ rendert sauber. Math-Schrift ist konventionell richtig fuer
    # Standardabweichungs-σ in Statistik (Italic-Shape).
    "STIXTwoMath": "stix-two/STIXTwoMath-Regular.ttf",
    # Helvetica/Arial-Aliasse fuer ReportLab-Default-Compat (Geist substituiert).
    # v0.15.0: Kursiv bleibt in der Grotesk (bis 0.14.2 sprang es in Source Serif —
    # damals gab es keinen kursiven Geist-Schnitt).
    "Helvetica": "geist/Geist-Regular.ttf",
    "Helvetica-Bold": "geist/Geist-Bold.ttf",
    "Helvetica-Oblique": "geist/Geist-Italic.ttf",
    "Helvetica-BoldOblique": "geist/Geist-BoldItalic.ttf",
    "Arial": "geist/Geist-Regular.ttf",
    "Arial-Bold": "geist/Geist-Bold.ttf",
    "Arial-Italic": "geist/Geist-Italic.ttf",
    "Arial-BoldItalic": "geist/Geist-BoldItalic.ttf",
}

# Familien-Zuordnung fuer <b>/<i> (v0.15.0): (normal, fett, kursiv, fett-kursiv).
# Fehlt einer Familie ein Schnitt, steht der naechstliegende VORHANDENE da und der
# Kommentar sagt es — nie ein stiller Grundschnitt.
_FAMILIEN: dict[str, tuple[str, str, str, str]] = {
    "Geist": ("Geist", "Geist-Bold", "Geist-Italic", "Geist-BoldItalic"),
    # Medium als Grundschrift (z. B. Status-Zeilen): Kursiv bleibt im Medium-Gewicht.
    "Geist-Medium": (
        "Geist-Medium",
        "Geist-Bold",
        "Geist-MediumItalic",
        "Geist-BoldItalic",
    ),
    "SourceSerif": (
        "SourceSerif",
        "SourceSerif-Bold",
        "SourceSerif-Italic",
        "SourceSerif-BoldItalic",
    ),
    # Zitat-Kursive als GRUNDSCHRIFT (v0.16.0, font_family("italic-editorial")): der
    # Grundschnitt ist schon kursiv, also ist Kursiv derselbe Schnitt und <b> ergibt
    # Fett-Kursiv. Bis 0.15.0 war der Name keine Familie — <b> ging still verloren.
    "SourceSerif4-Italic": (
        "SourceSerif4-Italic",
        "SourceSerif4-BoldItalic",
        "SourceSerif4-Italic",
        "SourceSerif4-BoldItalic",
    ),
    "SourceSans": (
        "SourceSans",
        "SourceSans-Bold",
        "SourceSans-Italic",
        "SourceSans-BoldItalic",
    ),
    "Inter": ("Inter", "Inter-Bold", "Inter-Italic", "Inter-BoldItalic"),
    "NotoSans": ("NotoSans", "NotoSans-Bold", "NotoSans-Italic", "NotoSans-BoldItalic"),
    # Kein Fett-Kursiv-Schnitt im Paket: Fett gewinnt.
    "STIXTwo": ("STIXTwo", "STIXTwo-Bold", "STIXTwo-Italic", "STIXTwo-Bold"),
    "STIXTwoText": (
        "STIXTwoText",
        "STIXTwoText-Bold",
        "STIXTwoText-Italic",
        "STIXTwoText-Bold",
    ),
    # Nur aufrecht und fett im Paket; Code wird nicht kursiv gesetzt (<i> bleibt aufrecht,
    # <b><i> wird fett).
    "JetBrainsMono": (
        "JetBrainsMono",
        "JetBrainsMono-Bold",
        "JetBrainsMono",
        "JetBrainsMono-Bold",
    ),
    # Die Ersatznamen der ReportLab-Standardschrift bilden eine Familie wie Geist.
    "Helvetica": (
        "Helvetica",
        "Helvetica-Bold",
        "Helvetica-Oblique",
        "Helvetica-BoldOblique",
    ),
    "Arial": ("Arial", "Arial-Bold", "Arial-Italic", "Arial-BoldItalic"),
}


def register_all_fonts() -> list[str]:
    """Registriert alle Default-Fonts beim ReportLab.

    Returns:
        Liste der erfolgreich registrierten Namen.
    """
    registered: list[str] = []
    for name, rel_path in _FONT_MAP.items():
        full_path = FONT_DIR / rel_path
        if not full_path.is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont(name, str(full_path)))
            registered.append(name)
        except Exception as exc:  # noqa: BLE001 — ReportLab kann diverse Fehler werfen
            # Nicht verschlucken (bis 0.15.0: ``pass``): ein unlesbarer Schnitt faellt
            # sonst erst beim Rendern als „Font not registered“ auf.
            _LOG.warning("Schrift %s (%s) nicht angemeldet: %s", name, full_path, exc)
    angemeldet = set(registered)
    for familie, (normal, fett, kursiv, fettkursiv) in _FAMILIEN.items():
        # Nur vollstaendig registrierte Familien: eine halbe Zuordnung wuerde beim
        # Rendern auf einen unbekannten Namen zeigen.
        if {normal, fett, kursiv, fettkursiv} <= angemeldet:
            pdfmetrics.registerFontFamily(
                familie, normal=normal, bold=fett, italic=kursiv, boldItalic=fettkursiv
            )
    return registered


def font_path(name: str) -> Path | None:
    """Liefert absoluten Pfad zur TTF-Datei eines registrierten Fonts.

    Returns:
        Path-Objekt oder None falls Name unbekannt.
    """
    rel = _FONT_MAP.get(name)
    if not rel:
        return None
    full = FONT_DIR / rel
    return full if full.is_file() else None


__all__ = ["FONT_DIR", "font_path", "register_all_fonts"]
