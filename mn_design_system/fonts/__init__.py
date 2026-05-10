"""Font-Registration fuer ReportLab.

Public-API:
    from mn_design_system.fonts import register_all_fonts, FONT_DIR
    register_all_fonts()  # einmal beim App-Start

Registriert alle TTF-Files unter mn_design_system/fonts/ beim ReportLab.
Idempotent: mehrfache Aufrufe sind harmlos (ReportLab ueberschreibt).
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
    "SourceSerif": "source-serif/SourceSerif4-Regular.ttf",
    "SourceSerif-Italic": "source-serif/SourceSerif4-Italic.ttf",
    "SourceSerif-Bold": "source-serif/SourceSerif4-Bold.ttf",
    "SourceSerif-BoldItalic": "source-serif/SourceSerif4-BoldItalic.ttf",
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
    "STIXTwo-BoldItalic": "stix-two/STIXTwoText-BoldItalic.ttf",
    # Aliase fuer helpers.font_with_fallback-Output (S249, macb-claude):
    # font_with_fallback wrappt Greek-Chars in <font name="STIXTwoText">...</font>,
    # daher muss der lange Name auch in pdfmetrics aufloesbar sein. Sonst
    # ValueError beim PDF-Render (Bug-Trail: claudeAI daily-engine 2026-05-10).
    "STIXTwoText": "stix-two/STIXTwoText-Regular.ttf",
    "STIXTwoText-Italic": "stix-two/STIXTwoText-Italic.ttf",
    "STIXTwoText-Bold": "stix-two/STIXTwoText-Bold.ttf",
    "STIXTwoText-BoldItalic": "stix-two/STIXTwoText-BoldItalic.ttf",
    # Helvetica/Arial-Aliasse fuer ReportLab-Default-Compat (Geist substituiert)
    "Helvetica": "geist/Geist-Regular.ttf",
    "Helvetica-Bold": "geist/Geist-Bold.ttf",
    "Helvetica-Oblique": "source-serif/SourceSerif4-Italic.ttf",
    "Helvetica-BoldOblique": "source-serif/SourceSerif4-BoldItalic.ttf",
    "Arial": "geist/Geist-Regular.ttf",
    "Arial-Bold": "geist/Geist-Bold.ttf",
    "Arial-Italic": "source-serif/SourceSerif4-Italic.ttf",
    "Arial-BoldItalic": "source-serif/SourceSerif4-BoldItalic.ttf",
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
        except Exception:  # noqa: BLE001 — ReportLab kann diverse Fehler werfen
            pass
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


__all__ = ["register_all_fonts", "font_path", "FONT_DIR"]
