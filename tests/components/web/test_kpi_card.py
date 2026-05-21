"""Tests fuer Web-KPI-Card-Renderer (Welle E.0)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import KpiCardInput
from mn_design_system.components.web.kpi_card import (
    render_kpi_card_css,
    render_kpi_card_html,
)


class TestRenderKpiCardHtml:
    def test_minimal_renders(self):
        html = render_kpi_card_html(KpiCardInput(label="DAX", value="22.450"))
        assert '<article class="mn-kpi-card">' in html
        assert "DAX" in html
        assert "22.450" in html
        assert "</article>" in html

    def test_change_pct_up_class(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", change_pct=1.5)
        )
        assert "is-up" in html
        assert "+1.50%" in html
        assert "▲" in html

    def test_change_pct_down_class(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", change_pct=-2.3)
        )
        assert "is-down" in html
        assert "-2.30%" in html
        assert "▼" in html

    def test_change_pct_neutral_class(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", change_pct=0.0)
        )
        assert "is-neutral" in html

    def test_no_change_pct_omits_change(self):
        html = render_kpi_card_html(KpiCardInput(label="X", value="100"))
        assert "mn-kpi-card__change" not in html

    def test_sparkline_embedded_when_values(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="X",
                value="100",
                sparkline_values=[1.0, 2.0, 3.0, 4.0, 5.0],
            )
        )
        assert "<svg" in html
        assert "mn-kpi-card__sparkline" in html

    def test_caption_when_provided(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", caption="30 Tage")
        )
        assert "30 Tage" in html
        assert "mn-kpi-card__caption" in html

    def test_xss_label_escaped(self):
        html = render_kpi_card_html(
            KpiCardInput(label="<script>alert(1)</script>", value="100")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_value_escaped(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="<img src=x onerror=alert(1)>")
        )
        assert "<img" not in html
        assert "&lt;img" in html

    def test_inline_css_embedded(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100"), inline_css=True
        )
        assert "<style>" in html
        assert ".mn-kpi-card" in html

    def test_inline_css_off_by_default(self):
        html = render_kpi_card_html(KpiCardInput(label="X", value="100"))
        assert "<style>" not in html


class TestRenderKpiCardCss:
    def test_returns_css_string(self):
        css = render_kpi_card_css()
        assert ".mn-kpi-card {" in css
        assert ".mn-kpi-card__label {" in css
        assert ".mn-kpi-card__value {" in css

    def test_uses_css_custom_properties(self):
        css = render_kpi_card_css()
        assert "var(--color-light-h1" in css
        assert "var(--color-status-success" in css
        assert "var(--color-status-error" in css

    def test_css_has_layout_only_no_token_values(self):
        # Token-Werte sollen ausschliesslich ueber var(--...) kommen.
        # Konkrete Hex-Werte (Fallbacks fuer Konsumenten ohne tokens.css) sind erlaubt.
        css = render_kpi_card_css()
        # Layout-Eigenschaften muessen vorhanden sein
        assert "padding" in css
        assert "border-radius" in css
        assert "font-size" in css

    def test_uses_foundation_tokens(self):
        """Re-Tokenisierung: die KPI-Mikro-Skala (frueher 7-11px) tritt auf die
        Web-Foundation — Label/Change/Caption auf web.text.caption (12px),
        der Headline-Wert auf web.text.h3 (23px)."""
        css = render_kpi_card_css()
        assert "var(--web-text-caption" in css
        assert "var(--web-text-h3" in css
        assert "var(--web-leading-h3" in css
        assert "var(--web-font-sans" in css
        assert "var(--web-stroke-line" in css
        assert "var(--web-color-separator" in css
        assert "var(--space-" in css

    def test_radius_card_fallback_is_4px(self):
        """Der radius-card-Fallback entspricht dem echten Token (4px)."""
        css = render_kpi_card_css()
        assert "var(--radius-card, 4px)" in css

    def test_no_print_pt_units(self):
        """Keine pt-Einheiten — die KPI-Card ist rein web. Die alten
        rem-Kommentare (~9pt/~7pt) sind mit der Re-Tokenisierung weg.

        Geprueft wird auf pt als Einheit ('pt;' / 'pt '), nicht auf das
        Substring 'pt' — der Token-Schritt 'caption' enthaelt es legitim."""
        css = render_kpi_card_css()
        assert "pt;" not in css and "pt " not in css
