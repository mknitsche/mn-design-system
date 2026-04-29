"""Web-Renderer Sparkline — SVG-Output, Welle E.0 (S238).

Konsumiert SparklineInput aus `_patterns.contracts`. Liefert
einen self-contained SVG-String, der direkt in HTML eingebettet werden kann.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import SparklineInput
from mn_design_system.tokens import get as token_get

DEFAULT_STROKE_WIDTH = 1.2


def render_sparkline_svg(input: SparklineInput) -> str:
    """SVG-Sparkline aus SparklineInput.

    Die Token-Defaults (color.light.h2 fuer Linie) gelten symmetrisch zur
    PDF-Implementierung. Konsumenten koennen via input.color ueberschreiben.
    """
    width = input.width
    height = input.height
    stroke = input.color or token_get("color.light.h2")

    values = list(input.values)
    n = len(values)
    if n < 2:
        return ""

    vmin = min(values)
    vmax = max(values)
    span = vmax - vmin
    if span <= 0:
        # Flache Linie auf Mittelhoehe
        y_mid = height / 2
        d = f"M 0 {y_mid:.2f} L {width:.2f} {y_mid:.2f}"
    else:
        step_x = width / (n - 1)
        points = []
        for i, v in enumerate(values):
            x = i * step_x
            y = height - (v - vmin) / span * height
            points.append(f"{x:.2f} {y:.2f}")
        d = "M " + " L ".join(points)

    safe_stroke = escape(stroke, quote=True)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width:.2f}" height="{height:.2f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}" '
        f'class="mn-sparkline" '
        f'aria-hidden="true">'
        f'<path d="{d}" fill="none" stroke="{safe_stroke}" '
        f'stroke-width="{DEFAULT_STROKE_WIDTH}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f"</svg>"
    )
