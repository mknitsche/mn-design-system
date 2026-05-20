"""Tests fuer Web-Wetter-Strip-Renderer (Welle E.0)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    WetterCategory,
    WetterDay,
    WetterStripInput,
)
from mn_design_system.components.web.wetter_strip import (
    render_wetter_strip_css,
    render_wetter_strip_html,
)


def _make_input(**overrides) -> WetterStripInput:
    base = {
        "location": "Nuernberg",
        "days": [
            WetterDay(
                header_label="Heute",
                category=WetterCategory.SONNIG,
                temp_min_c=8,
                temp_max_c=18,
                precip_pct=10,
            ),
            WetterDay(
                header_label="Mi",
                category=WetterCategory.REGEN,
                temp_min_c=6,
                temp_max_c=14,
                precip_pct=80,
            ),
            WetterDay(
                header_label="Do",
                category=WetterCategory.BEWOELKT,
                temp_min_c=7,
                temp_max_c=16,
                precip_pct=30,
            ),
        ],
    }
    base.update(overrides)
    return WetterStripInput(**base)


class TestRenderWetterStripHtml:
    def test_minimal_renders(self):
        html = render_wetter_strip_html(_make_input())
        assert '<section class="mn-wetter-strip"' in html
        assert "Nuernberg" in html
        assert "Heute" in html
        assert "Mi" in html
        assert "Do" in html
        assert "</section>" in html

    def test_three_days_rendered(self):
        html = render_wetter_strip_html(_make_input())
        assert html.count("mn-wetter-strip__day-label") == 3
        assert html.count("mn-wetter-strip__icon") == 3
        assert html.count("mn-wetter-strip__temp") == 3
        assert html.count("mn-wetter-strip__precip") == 3

    def test_phosphor_icon_classes(self):
        html = render_wetter_strip_html(_make_input())
        assert "ph-sun" in html
        assert "ph-cloud-rain" in html
        assert "ph-cloud" in html

    def test_temperatures_rendered(self):
        html = render_wetter_strip_html(_make_input())
        assert "18°" in html
        assert "8°" in html
        assert "14°" in html

    def test_precip_rendered(self):
        html = render_wetter_strip_html(_make_input())
        assert "10%" in html
        assert "80%" in html
        assert "30%" in html

    def test_summary_text_when_provided(self):
        html = render_wetter_strip_html(
            _make_input(summary_text="Wechselhafte Woche mit Schauern.")
        )
        assert "Wechselhafte Woche" in html
        assert "mn-wetter-strip__summary" in html

    def test_summary_omitted_when_none(self):
        html = render_wetter_strip_html(_make_input())
        assert "mn-wetter-strip__summary" not in html

    def test_xss_summary_escaped(self):
        html = render_wetter_strip_html(
            _make_input(summary_text="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_location_escaped(self):
        html = render_wetter_strip_html(_make_input(location="<b>NBG</b>"))
        assert "<b>NBG</b>" not in html
        assert "&lt;b&gt;NBG" in html

    def test_screen_reader_label_per_icon(self):
        html = render_wetter_strip_html(_make_input())
        assert html.count("mn-wetter-strip__sr") == 3
        assert "sonnig" in html
        assert "regen" in html

    def test_inline_css_embedded(self):
        html = render_wetter_strip_html(_make_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-wetter-strip" in html


class TestRenderWetterStripCss:
    def test_returns_css(self):
        css = render_wetter_strip_css()
        assert ".mn-wetter-strip {" in css
        assert ".mn-wetter-strip__grid {" in css

    def test_uses_css_custom_properties(self):
        css = render_wetter_strip_css()
        assert "var(--color-light-h1" in css
        assert "var(--color-status-success" in css
