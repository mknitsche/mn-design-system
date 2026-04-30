"""TDD-Tests fuer KPI-Card PDF-Implementierung (Welle B v0.2.0)."""

from __future__ import annotations

import pytest
from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
)
from mn_design_system.components.pdf.kpi_card import build_kpi_card
from pydantic import ValidationError
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Paragraph, Spacer

# ---------------------------------------------------------------------------
# Contract-Validation
# ---------------------------------------------------------------------------


class TestKpiCardContract:
    def test_minimal_valid(self):
        inp = KpiCardInput(label="DAX", value="22.450")
        assert inp.change_pct is None
        assert inp.sparkline_values is None

    def test_all_fields(self):
        inp = KpiCardInput(
            label="Bitcoin",
            value="75.991,58",
            change_pct=-0.43,
            sparkline_values=[1.0, 2.0, 3.0],
            caption="Stand: 04:50",
        )
        assert inp.change_pct == -0.43

    def test_label_required(self):
        with pytest.raises(ValidationError):
            KpiCardInput(label="", value="100")

    def test_value_required(self):
        with pytest.raises(ValidationError):
            KpiCardInput(label="DAX", value="")

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            KpiCardInput(label="DAX", value="100", foo="bar")


# ---------------------------------------------------------------------------
# Trend-Direction-Helper
# ---------------------------------------------------------------------------


class TestTrendDirection:
    def test_up(self):
        inp = KpiCardInput(label="X", value="1", change_pct=2.5)
        assert inp.trend_direction() == KpiTrendDirection.UP

    def test_down(self):
        inp = KpiCardInput(label="X", value="1", change_pct=-2.5)
        assert inp.trend_direction() == KpiTrendDirection.DOWN

    def test_neutral_zero(self):
        inp = KpiCardInput(label="X", value="1", change_pct=0.0)
        assert inp.trend_direction() == KpiTrendDirection.NEUTRAL

    def test_neutral_none(self):
        inp = KpiCardInput(label="X", value="1", change_pct=None)
        assert inp.trend_direction() == KpiTrendDirection.NEUTRAL

    def test_neutral_micro(self):
        """abs(change) < 0.01 → NEUTRAL (kein UP/DOWN bei Mikro-Bewegung)."""
        inp = KpiCardInput(label="X", value="1", change_pct=0.005)
        assert inp.trend_direction() == KpiTrendDirection.NEUTRAL


# ---------------------------------------------------------------------------
# Build-Output
# ---------------------------------------------------------------------------


class TestBuildKpiCard:
    def test_returns_5_flowables(self):
        """Card hat 5 Flowables: label, value, change, sparkline, caption."""
        inp = KpiCardInput(label="DAX", value="22.450")
        result = build_kpi_card(inp)
        assert len(result) == 5

    def test_label_paragraph(self):
        inp = KpiCardInput(label="Bitcoin", value="75.991")
        result = build_kpi_card(inp)
        assert isinstance(result[0], Paragraph)
        assert result[0].text == "Bitcoin"

    def test_value_paragraph(self):
        inp = KpiCardInput(label="DAX", value="22.450,12")
        result = build_kpi_card(inp)
        assert isinstance(result[1], Paragraph)
        assert "22.450,12" in result[1].text

    def test_change_positive(self):
        inp = KpiCardInput(label="X", value="100", change_pct=1.25)
        result = build_kpi_card(inp)
        change_text = result[2].text
        assert "▲" in change_text
        assert "+1,25%" in change_text  # deutsche Notation

    def test_change_negative(self):
        inp = KpiCardInput(label="X", value="100", change_pct=-0.75)
        result = build_kpi_card(inp)
        change_text = result[2].text
        assert "▼" in change_text
        assert "-0,75%" in change_text

    def test_change_none_empty(self):
        inp = KpiCardInput(label="X", value="100", change_pct=None)
        result = build_kpi_card(inp)
        assert result[2].text == ""

    # ---- v0.4.1 / S239 B5: Drei-Stufen-Schwellwert ----

    def test_change_below_threshold_positive_is_muted(self):
        """|Δ|<0.5% positiv → muted (grau), Bullet-Punkt, kein Pfeil."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.30)
        text = build_kpi_card(inp)[2].text
        assert "▲" not in text
        assert "•" in text
        assert "+0,30%" in text
        # color.viz.muted = #b0bec5
        assert "b0bec5" in text.lower()

    def test_change_below_threshold_negative_is_muted(self):
        """|Δ|<0.5% negativ → muted (grau), Bullet, kein Pfeil. Sign manuell."""
        inp = KpiCardInput(label="X", value="100", change_pct=-0.20)
        text = build_kpi_card(inp)[2].text
        assert "▼" not in text
        assert "•" in text
        assert "-0,20%" in text
        assert "b0bec5" in text.lower()

    def test_change_zero_is_muted(self):
        """change_pct=0.0 → muted, Bullet, +0,00%."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.0)
        text = build_kpi_card(inp)[2].text
        assert "▲" not in text and "▼" not in text
        assert "•" in text
        assert "+0,00%" in text

    def test_change_at_threshold_positive_is_strong(self):
        """change_pct=0.5 (genau Schwelle) → kraeftig, Pfeil, success-color."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.5)
        text = build_kpi_card(inp)[2].text
        assert "▲" in text
        assert "+0,50%" in text
        # color.status.success = #2e7d32
        assert "2e7d32" in text.lower()

    def test_change_at_threshold_negative_is_strong(self):
        inp = KpiCardInput(label="X", value="100", change_pct=-0.5)
        text = build_kpi_card(inp)[2].text
        assert "▼" in text
        assert "-0,50%" in text
        assert "d32f2f" in text.lower()

    def test_change_just_below_threshold_is_muted(self):
        """0.499% (knapp unter 0.5%) bleibt muted."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.499)
        text = build_kpi_card(inp)[2].text
        assert "•" in text
        assert "▲" not in text

    def test_sparkline_with_values(self):
        inp = KpiCardInput(label="X", value="100", sparkline_values=[1.0, 2.0, 3.0, 4.0])
        result = build_kpi_card(inp)
        # Sparkline-Slot ist ein ReportLab Drawing
        assert isinstance(result[3], Drawing)

    def test_sparkline_without_values_is_spacer(self):
        inp = KpiCardInput(label="X", value="100", sparkline_values=None)
        result = build_kpi_card(inp)
        assert isinstance(result[3], Spacer)

    def test_sparkline_with_one_value_is_spacer(self):
        """Mit nur 1 Wert (zu wenig fuer Sparkline) wird Spacer genutzt."""
        inp = KpiCardInput(label="X", value="100", sparkline_values=[1.0])
        result = build_kpi_card(inp)
        assert isinstance(result[3], Spacer)

    def test_caption_string(self):
        inp = KpiCardInput(label="X", value="100", caption="Stand: 04:50")
        result = build_kpi_card(inp)
        assert isinstance(result[4], Paragraph)
        assert result[4].text == "Stand: 04:50"

    def test_caption_empty_when_none(self):
        inp = KpiCardInput(label="X", value="100", caption=None)
        result = build_kpi_card(inp)
        assert result[4].text == ""
