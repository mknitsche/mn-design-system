"""TDD-Tests fuer Sparkline-PDF-Implementierung (Welle B v0.2.0).

Prueft:
- Pydantic-Contract-Validierung
- Drawing-Output mit korrekter Groesse
- Adaptive Skala (Default, Min, Auto-Aufweitung)
- Default-Color via Token-Lookup
- Custom-Color via Hex-String
"""

from __future__ import annotations

import pytest
from mn_design_system.components._patterns.contracts import SparklineInput
from mn_design_system.components.pdf import build_sparkline
from mn_design_system.components.pdf.sparkline import _compute_skala
from pydantic import ValidationError
from reportlab.graphics.shapes import Drawing, PolyLine

# ---------------------------------------------------------------------------
# Contract-Validation
# ---------------------------------------------------------------------------


class TestSparklineInputContract:
    """Pydantic-Validierung des Inputs."""

    def test_valid_input(self):
        inp = SparklineInput(values=[1.0, 2.0, 3.0], width=80.0, height=20.0)
        assert inp.values == [1.0, 2.0, 3.0]
        assert inp.color is None

    def test_min_two_values_required(self):
        with pytest.raises(ValidationError):
            SparklineInput(values=[1.0], width=80.0, height=20.0)

    def test_positive_dimensions(self):
        with pytest.raises(ValidationError):
            SparklineInput(values=[1.0, 2.0], width=0.0, height=20.0)
        with pytest.raises(ValidationError):
            SparklineInput(values=[1.0, 2.0], width=80.0, height=-1.0)

    def test_frozen(self):
        inp = SparklineInput(values=[1.0, 2.0], width=80.0, height=20.0)
        with pytest.raises(ValidationError):
            inp.color = "#ff0000"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            SparklineInput(values=[1.0, 2.0], width=80.0, height=20.0, foo="bar")


# ---------------------------------------------------------------------------
# Drawing-Output
# ---------------------------------------------------------------------------


class TestBuildSparkline:
    """build_sparkline() liefert korrektes Drawing."""

    def test_returns_drawing(self):
        inp = SparklineInput(values=[1.0, 2.0, 3.0, 2.5], width=80.0, height=20.0)
        result = build_sparkline(inp)
        assert isinstance(result, Drawing)

    def test_dimensions(self):
        inp = SparklineInput(values=[1.0, 2.0], width=100.0, height=30.0)
        result = build_sparkline(inp)
        assert result.width == 100.0
        assert result.height == 30.0

    def test_contains_polyline(self):
        inp = SparklineInput(values=[1.0, 2.0, 3.0], width=80.0, height=20.0)
        result = build_sparkline(inp)
        polylines = [c for c in result.contents if isinstance(c, PolyLine)]
        assert len(polylines) == 1

    def test_polyline_point_count(self):
        """N values -> N (x, y) pairs -> 2N coordinates."""
        inp = SparklineInput(values=[1.0, 2.0, 3.0, 4.0, 5.0], width=80.0, height=20.0)
        result = build_sparkline(inp)
        polyline = next(c for c in result.contents if isinstance(c, PolyLine))
        assert len(polyline.points) == 10  # 5 values * 2 coords

    def test_custom_color_applied(self):
        inp = SparklineInput(values=[1.0, 2.0], width=80.0, height=20.0, color="#ff0000")
        result = build_sparkline(inp)
        polyline = next(c for c in result.contents if isinstance(c, PolyLine))
        # ReportLab HexColor("#ff0000") = (1.0, 0.0, 0.0) approx
        assert abs(polyline.strokeColor.red - 1.0) < 0.01
        assert abs(polyline.strokeColor.green - 0.0) < 0.01

    def test_default_color_from_token(self):
        """Ohne color-Arg wird color.light.h2 (Indigo-700) verwendet."""
        inp = SparklineInput(values=[1.0, 2.0], width=80.0, height=20.0)
        result = build_sparkline(inp)
        polyline = next(c for c in result.contents if isinstance(c, PolyLine))
        # Indigo-700 = #4338ca
        assert abs(polyline.strokeColor.red - 0x43 / 255.0) < 0.01


# ---------------------------------------------------------------------------
# Adaptive Skala
# ---------------------------------------------------------------------------


class TestAdaptiveSkala:
    """_compute_skala() Heuristik."""

    def test_default_10pct(self):
        # Range (101-99 = 2) ist zwischen 5% (5) und 10% (10) von 100
        skala_min, skala_max = _compute_skala([99, 100, 101], current=100.0)
        # In diesem Fall val_range=2, threshold_5=5, val_range < threshold_5 → ±5%
        assert skala_min == pytest.approx(95.0)
        assert skala_max == pytest.approx(105.0)

    def test_quiet_values_5pct(self):
        # Range 0.1, sehr ruhig, val_range < threshold_5 → ±5%
        skala_min, skala_max = _compute_skala([99.95, 100.0, 100.05], current=100.0)
        assert skala_min == pytest.approx(95.0)
        assert skala_max == pytest.approx(105.0)

    def test_auto_widening(self):
        # Range 75 (125-50), viel groesser als ±10% (10) → Auto-Aufweitung
        skala_min, skala_max = _compute_skala([50, 75, 100, 125], current=100.0)
        # Pad = val_range * 0.05 = 75 * 0.05 = 3.75
        assert skala_min == pytest.approx(46.25)
        assert skala_max == pytest.approx(128.75)

    def test_zero_or_negative_current(self):
        skala_min, skala_max = _compute_skala([1.0, 2.0], current=0.0)
        assert skala_min == 0.0
        assert skala_max == 1.0

    def test_empty_values(self):
        skala_min, skala_max = _compute_skala([], current=100.0)
        assert skala_min == 0.0
        assert skala_max == 1.0


# ---------------------------------------------------------------------------
# Edge-Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_two_identical_values(self):
        """val_range=0, sollte trotzdem nicht crashen."""
        inp = SparklineInput(values=[100.0, 100.0], width=80.0, height=20.0)
        result = build_sparkline(inp)
        assert isinstance(result, Drawing)
