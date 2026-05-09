"""PDF-Implementierung des Wetter-Strip-Patterns (ReportLab native).

Pattern-Spec: components/_patterns/wetter_strip.md
Contract: components/_patterns/contracts.py::WetterStripInput

Liefert eine Liste von Flowables, die der Caller (z.B. Briefing-Renderer)
in die story einfuegt. Entscheidung gegen einen Composite-KeepTogether-Wrapper
gefallen, damit Caller selber entscheidet, ob Wetter-Strip mit Stale-Caption
zusammengehalten werden soll.
"""

from __future__ import annotations

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from mn_design_system.components._patterns.contracts import (
    WetterCategory,
    WetterStripInput,
)
from mn_design_system.tokens import get as token_get

# Phosphor-Codepoints fuer Wetter-Symbole (verifiziert via Phosphor.json).
_ICON_MAP: dict[WetterCategory, str] = {
    WetterCategory.SONNIG: "",  # sun
    WetterCategory.HEITER: "",  # cloud-sun
    WetterCategory.BEWOELKT: "",  # cloud
    WetterCategory.REGEN: "",  # cloud-rain
    WetterCategory.SCHNEE: "",  # cloud-snow
    WetterCategory.GEWITTER: "",  # lightning
    WetterCategory.NEBEL: "",  # cloud-fog
    WetterCategory.WIND: "",  # wind
}


def _parse_pt(token_str: str) -> float:
    """'10pt' -> 10.0 (S242: KT-1 design-system body-Token-Konsumtion)."""
    s = str(token_str).strip()
    return float(s[:-2]) if s.endswith("pt") else float(s)


def _build_styles() -> dict[str, ParagraphStyle]:
    """Komponenten-eigene Styles, gespeist aus Tokens."""
    color_h2 = token_get("color.light.h2", "#4338ca")
    color_h1 = token_get("color.light.h1", "#312e81")
    color_text_muted = token_get("color.light.text-muted", "#6b7280")
    # S242 KT-1: Summary-Text (Marktlage unter Strip) muss identisch zu allen
    # Body-Texten im Briefing sein — body-Token statt hardcoded 10/14.
    body_size = _parse_pt(token_get("font.size.body", "10pt"))
    body_lead = _parse_pt(token_get("font.leading.body", "13.5pt"))

    return {
        "icon": ParagraphStyle(
            "WetterStripIcon",
            fontName="Phosphor",
            fontSize=22,
            leading=26,
            textColor=HexColor(color_h2),
            alignment=TA_CENTER,
            spaceAfter=3 * mm,
        ),
        "label": ParagraphStyle(
            "WetterStripLabel",
            fontName="Geist-Bold",
            fontSize=9,
            leading=12,
            textColor=HexColor(color_h1),
            alignment=TA_CENTER,
            spaceAfter=1.5 * mm,
        ),
        "temp": ParagraphStyle(
            "WetterStripTemp",
            fontName="Geist",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=1 * mm,
        ),
        "precip": ParagraphStyle(
            "WetterStripPrecip",
            fontName="Geist",
            fontSize=8.5,
            leading=11,
            textColor=HexColor(color_text_muted),
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "summary": ParagraphStyle(
            "WetterStripSummary",
            fontName="Geist",
            fontSize=body_size,
            leading=body_lead,
            spaceBefore=2 * mm,
            spaceAfter=2 * mm,
        ),
    }


def build_wetter_strip(
    input: WetterStripInput,  # noqa: A002
    *,
    total_width: float = 170 * mm,
    column_width: float = 40 * mm,
) -> list[Flowable]:
    """Erzeugt Wetter-Strip-Flowables aus WetterStripInput.

    Args:
        input: Pydantic-Contract mit days, summary_text, location.
        total_width: Gesamtbreite (fuer Zentrierung des Strips).
        column_width: Breite pro Tageskachel.

    Returns:
        Liste von Flowables (Strip-Table + optional Summary-Paragraph).
    """
    styles = _build_styles()
    flowables: list[Flowable] = []

    # 1. Strip-Table mit den Tageskacheln
    col_data: list[list] = []
    for d in input.days:
        icon_char = _ICON_MAP.get(d.category, _ICON_MAP[WetterCategory.BEWOELKT])
        temp = f"{d.temp_min_c}° / {d.temp_max_c}°"
        precip = f"{d.precip_pct}%"
        cell = [
            Paragraph(icon_char, styles["icon"]),
            Paragraph(d.header_label, styles["label"]),
            Paragraph(temp, styles["temp"]),
            Paragraph(precip, styles["precip"]),
        ]
        col_data.append(cell)

    n_cols = len(col_data)
    used_w = column_width * n_cols
    side_pad = max(0.0, (total_width - used_w) / 2)
    cols = [side_pad, *([column_width] * n_cols), side_pad]
    row = ["", *col_data, ""]
    tbl = Table([row], colWidths=cols)
    tbl.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flowables.append(tbl)

    # 2. Optional Summary-Text
    if input.summary_text:
        flowables.append(Spacer(1, 1.5 * mm))
        flowables.append(Paragraph(_escape(input.summary_text), styles["summary"]))

    return flowables


def _escape(text: str) -> str:
    """Paragraph-sicheres Escaping."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


__all__ = ["build_wetter_strip"]
