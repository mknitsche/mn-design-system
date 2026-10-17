"""PDF-Implementierung des KPI-Card-Patterns (ReportLab native).

Pattern-Spec: components/_patterns/kpi_card.md
Contract: components/_patterns/contracts.py::KpiCardInput

Liefert die Flowables EINER KPI-Karte (Label, Value, Change, Sparkline, Caption).
Caller arrangiert mehrere Karten in einer Reihe (Briefing-Renderer macht das mit
Gap-Spalten fuer Tile-Look).
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Paragraph, Spacer

from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
    KpiWertung,
    SparklineInput,
)
from mn_design_system.components.pdf.sparkline import build_sparkline
from mn_design_system.helpers import font_family
from mn_design_system.tokens import get as token_get


def _build_styles() -> dict[str, ParagraphStyle]:
    """KPI-Card-Styles aus Tokens."""
    color_h1 = token_get("color.light.h1", "#312e81")
    color_text_muted = token_get("color.light.text-muted", "#6b7280")

    return {
        "label": ParagraphStyle(
            "KpiCardLabel",
            fontName=font_family("sans-bold"),
            fontSize=9,
            textColor=HexColor(color_h1),
            alignment=TA_LEFT,
            spaceAfter=1 * mm,
        ),
        "value": ParagraphStyle(
            "KpiCardValue",
            fontName=font_family("sans-bold"),
            fontSize=10,
            textColor=HexColor(color_h1),
            alignment=TA_RIGHT,
            spaceAfter=0.5 * mm,
        ),
        "change": ParagraphStyle(
            "KpiCardChange",
            fontName=font_family("sans"),
            fontSize=8,
            alignment=TA_RIGHT,
            spaceAfter=1 * mm,
        ),
        "caption": ParagraphStyle(
            "KpiCardCaption",
            fontName=font_family("italic-editorial"),
            fontSize=7,
            textColor=HexColor(color_text_muted),
            alignment=TA_LEFT,
            spaceBefore=0.5 * mm,
            spaceAfter=0,
        ),
    }


def _format_change(input: KpiCardInput) -> str:
    """Change mit Trend-Pfeil und Farbe (deutsche Komma-Notation).

    v0.4.3 (S241 KT-1 B-7): Glyph konsistent in allen 3 Stufen, nur Farbe variiert.
      - |Δ| < 0.5%   → muted (grau, `color.viz.muted`), ▲/▼ in voller Groesse.
        KT-1 S241 Briefing-Befund: Bullet "•" wirkte visuell deutlich kleiner
        als die Triangle-Glyphen — Lesbarkeit litt. Konsistente Pfeil-Groesse
        bei allen Stufen, der dezente Status wird ueber die Farbe transportiert.
      - |Δ| >= 0.5%, change >= 0 → success (▲), gruen.
      - |Δ| >= 0.5%, change <  0 → error (▼), rot.

    v0.17.1: die Farbe folgt der Wertung (Bewegung x Polaritaet ``richtung``): bei
    ``richtung="niedriger"`` ist ein Rueckgang gruen, bei ``"neutral"`` bleibt alles
    gedaempft. Mit ``delta_wert`` steht das deutsch formatierte absolute Delta
    („−1,2 kg") statt des Prozentwerts; rundet es auf null, steht „unverändert" ohne
    Pfeil. Ohne die neuen Felder ist die Ausgabe die von 0.17.0.
    """
    delta = input.delta_text()
    if delta is None and input.change_pct is None:
        return ""
    wertung = input.wertung()
    if wertung == KpiWertung.GUT:
        color = token_get("color.status.success", "#2e7d32")
    elif wertung == KpiWertung.SCHLECHT:
        color = token_get("color.status.error", "#D32F2F")
    else:
        color = token_get("color.viz.muted", "#b0bec5")
    if delta is not None:
        direction = input.trend_direction()
        glyph = {"up": "▲ ", "down": "▼ ", "neutral": ""}[direction.value]
        # Das Delta ist schon deutsch gesetzt (Tausenderpunkt!): kein `.`→`,` darueber.
        return f'<font color="{color}">{glyph}{escape(delta)}</font>'
    change_pct = input.change_pct
    glyph = "▲" if change_pct >= 0 else "▼"
    sign = "+" if change_pct >= 0 else ""
    s = f'<font color="{color}">{glyph} {sign}{change_pct:.2f}%</font>'
    return s.replace(".", ",")


def build_kpi_card(
    input: KpiCardInput,
    *,
    sparkline_width: float = 28 * mm,
    sparkline_height: float = 8 * mm,
) -> list[Flowable]:
    """Erzeugt KPI-Karten-Flowables.

    Args:
        input: Pydantic-Contract mit label, value, change_pct, sparkline_values, caption
            (seit 0.17.1 auch richtung, delta_wert, delta_einheit, dezimalstellen).
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
        Paragraph(_format_change(input), styles["change"]),
        sparkline,
        Paragraph(input.caption or "", styles["caption"]),
    ]


__all__ = ["KpiTrendDirection", "build_kpi_card"]
