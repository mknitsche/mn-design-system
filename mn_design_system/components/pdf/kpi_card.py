"""PDF-Implementierung des KPI-Card-Patterns (ReportLab native).

Pattern-Spec: components/_patterns/kpi_card.md
Contract: components/_patterns/contracts.py::KpiCardInput

Liefert die Flowables EINER KPI-Karte (Label, Value, Change, Sparkline, Caption).
Caller arrangiert mehrere Karten in einer Reihe (Briefing-Renderer macht das mit
Gap-Spalten fuer Tile-Look).
"""

from __future__ import annotations

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Paragraph, Spacer

from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
    SparklineInput,
)
from mn_design_system.components.pdf.sparkline import build_sparkline
from mn_design_system.tokens import get as token_get


def _build_styles() -> dict[str, ParagraphStyle]:
    """KPI-Card-Styles aus Tokens."""
    color_h1 = token_get("color.light.h1", "#312e81")
    color_text_muted = token_get("color.light.text-muted", "#6b7280")

    return {
        "label": ParagraphStyle(
            "KpiCardLabel",
            fontName="Geist-Bold",
            fontSize=9,
            textColor=HexColor(color_h1),
            alignment=TA_LEFT,
            spaceAfter=1 * mm,
        ),
        "value": ParagraphStyle(
            "KpiCardValue",
            fontName="Geist-Bold",
            fontSize=10,
            textColor=HexColor(color_h1),
            alignment=TA_RIGHT,
            spaceAfter=0.5 * mm,
        ),
        "change": ParagraphStyle(
            "KpiCardChange",
            fontName="Geist",
            fontSize=8,
            alignment=TA_RIGHT,
            spaceAfter=1 * mm,
        ),
        "caption": ParagraphStyle(
            "KpiCardCaption",
            fontName="SourceSerif-Italic",
            fontSize=7,
            textColor=HexColor(color_text_muted),
            alignment=TA_LEFT,
            spaceBefore=0.5 * mm,
            spaceAfter=0,
        ),
    }


def _format_change(change_pct: float | None) -> str:
    """Change-Pct mit Trend-Pfeil und Farbe (deutsche Komma-Notation)."""
    if change_pct is None:
        return ""
    color_success = token_get("color.status.success", "#2e7d32")
    color_error = token_get("color.status.error", "#D32F2F")
    if change_pct >= 0:
        s = f'<font color="{color_success}">▲ +{change_pct:.2f}%</font>'
    else:
        s = f'<font color="{color_error}">▼ {change_pct:.2f}%</font>'
    return s.replace(".", ",")


def build_kpi_card(
    input: KpiCardInput,  # noqa: A002
    *,
    sparkline_width: float = 28 * mm,
    sparkline_height: float = 8 * mm,
) -> list[Flowable]:
    """Erzeugt KPI-Karten-Flowables.

    Args:
        input: Pydantic-Contract mit label, value, change_pct, sparkline_values, caption.
        sparkline_width / sparkline_height: optional Sparkline-Dimension.

    Returns:
        Liste der 5 Flowables (label, value, change, sparkline, caption).
        Caller packt sie in eine Tabellen-Cell oder Frame.
    """
    styles = _build_styles()

    # Sparkline: build oder Spacer-Platzhalter
    if input.sparkline_values and len(input.sparkline_values) >= 2:
        sparkline: Flowable = build_sparkline(
            SparklineInput(
                values=input.sparkline_values,
                width=sparkline_width,
                height=sparkline_height,
            )
        )
    else:
        sparkline = Spacer(1, sparkline_height)

    return [
        Paragraph(input.label, styles["label"]),
        Paragraph(input.value, styles["value"]),
        Paragraph(_format_change(input.change_pct), styles["change"]),
        sparkline,
        Paragraph(input.caption or "", styles["caption"]),
    ]


__all__ = ["KpiTrendDirection", "build_kpi_card"]
