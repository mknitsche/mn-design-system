"""Tests fuer Web-Sparkline-Renderer (Welle E.0)."""

from __future__ import annotations

import re

from mn_design_system.components._patterns.contracts import SparklineInput
from mn_design_system.components.web.sparkline import render_sparkline_svg


class TestRenderSparklineSvg:
    def test_minimal_two_points(self):
        svg = render_sparkline_svg(SparklineInput(values=[1.0, 2.0], width=100, height=20))
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'width="100' in svg
        assert 'height="20' in svg
        assert "<path" in svg

    def test_default_color_from_token(self):
        svg = render_sparkline_svg(SparklineInput(values=[1.0, 2.0, 3.0], width=100, height=20))
        # Default ist color.light.h2 = #4338ca
        assert "#4338ca" in svg

    def test_custom_color(self):
        svg = render_sparkline_svg(
            SparklineInput(
                values=[1.0, 2.0, 3.0],
                width=100,
                height=20,
                color="#ff0000",
            )
        )
        assert "#ff0000" in svg

    def test_flat_line_renders_horizontal(self):
        svg = render_sparkline_svg(SparklineInput(values=[5.0, 5.0, 5.0], width=100, height=20))
        # M 0 10 L 100 10 — horizontal in der Mitte
        assert re.search(r"M\s+0\s+10", svg)

    def test_path_has_n_points(self):
        svg = render_sparkline_svg(
            SparklineInput(values=[1.0, 2.0, 3.0, 4.0], width=120, height=24)
        )
        # 4 Werte -> M + 3 L
        l_count = svg.count(" L ")
        assert l_count == 3

    def test_html_safe_color_escape(self):
        # Falls jemand boeses Hex-Format injection probiert
        svg = render_sparkline_svg(
            SparklineInput(
                values=[1.0, 2.0],
                width=100,
                height=20,
                color='" onerror="alert(1)',
            )
        )
        assert "onerror" not in svg or "&quot;" in svg
