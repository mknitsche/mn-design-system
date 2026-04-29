"""PDF-Implementierung des Sparkline-Patterns (ReportLab native).

Pattern-Spec: components/_patterns/sparkline.md
Contract: components/_patterns/contracts.py::SparklineInput

Adaptive Skalierung:
- Default: ±10% vom letzten Wert
- Min: ±5% bei sehr ruhigen Werten
- Auto-Aufweitung wenn 30-Tage-Range > ±10%

Kein matplotlib (zu schwer). ReportLab-native ~2ms/Sparkline.
"""

from __future__ import annotations

from reportlab.graphics.shapes import Drawing, PolyLine
from reportlab.lib.colors import Color, HexColor

from mn_design_system.components._patterns.contracts import SparklineInput
from mn_design_system.tokens import get as token_get

DEFAULT_LINE_WIDTH = 0.6
_DEFAULT_COLOR_TOKEN = "color.light.h2"
_DEFAULT_COLOR_FALLBACK = "#4338ca"


def build_sparkline(input: SparklineInput) -> Drawing:  # noqa: A002
    """Erzeugt Sparkline-Drawing aus SparklineInput.

    Args:
        input: Pydantic-Contract mit values, width, height, color (optional).

    Returns:
        ReportLab Drawing mit PolyLine.
    """
    drawing = Drawing(width=input.width, height=input.height)
    if len(input.values) < 2:
        return drawing

    current = input.values[-1]
    skala_min, skala_max = _compute_skala(input.values, current)
    skala_range = skala_max - skala_min if skala_max > skala_min else 1.0

    n = len(input.values)
    points: list[float] = []
    for i, v in enumerate(input.values):
        x = (i / (n - 1)) * input.width
        y_norm = (v - skala_min) / skala_range
        y_norm = max(0.0, min(1.0, y_norm))
        y = y_norm * input.height
        points.extend([x, y])

    color_str = input.color or token_get(_DEFAULT_COLOR_TOKEN, _DEFAULT_COLOR_FALLBACK)
    stroke = HexColor(color_str) if isinstance(color_str, str) else color_str
    line = PolyLine(
        points,
        strokeColor=stroke,
        strokeWidth=DEFAULT_LINE_WIDTH,
    )
    drawing.add(line)
    return drawing


def _compute_skala(values: list[float], current: float) -> tuple[float, float]:
    """Adaptive Skala.

    Default: ±10% vom current.
    Min ±5% bei sehr ruhigen Werten.
    Auto-Aufweitung wenn 30-Tage-Range groesser als ±10%.
    """
    if not values or current <= 0:
        return (0.0, 1.0)

    val_min = min(values)
    val_max = max(values)
    val_range = val_max - val_min

    threshold_10 = current * 0.10
    threshold_5 = current * 0.05

    if val_range <= threshold_10 and val_range >= threshold_5:
        return (current * 0.90, current * 1.10)
    if val_range < threshold_5:
        return (current * 0.95, current * 1.05)
    # Auto-Aufweitung
    pad = val_range * 0.05
    return (val_min - pad, val_max + pad)


__all__ = ["Color", "Drawing", "build_sparkline"]
