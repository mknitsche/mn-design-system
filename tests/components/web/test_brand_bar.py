"""Tests fuer Web-Brand-Bar-Renderer (UX-Welle v0.2, L2 Status)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    BrandBarChip,
    BrandBarInput,
    WebTier,
)
from mn_design_system.components.web.brand_bar import (
    render_brand_bar_css,
    render_brand_bar_html,
)


def _make_input(**overrides) -> BrandBarInput:
    base = {
        "brand_text": "mkn-desk",
        "chips": [
            BrandBarChip(tier=WebTier.BIBLIOTHEK, label="Bibliothek"),
            BrandBarChip(tier=WebTier.KABINETT, label="Owner"),
        ],
    }
    base.update(overrides)
    return BrandBarInput(**base)


class TestRenderBrandBarHtml:
    def test_minimal_renders(self):
        html = render_brand_bar_html(_make_input())
        assert 'class="mn-brand-bar"' in html
        assert "mkn-desk" in html

    def test_chips_rendered(self):
        # 2 Chip-Elemente: jeder bordered Tier-Chip traegt genau 1x die
        # Element-Klasse "mn-tier-chip--bordered" (die Basis-Klasse
        # "mn-tier-chip" + Tier-Modifier kaemen je 3x pro Chip).
        html = render_brand_bar_html(_make_input())
        assert html.count("mn-tier-chip--bordered") == 2
        assert "Bibliothek" in html
        assert "Owner" in html

    def test_chips_bordered(self):
        html = render_brand_bar_html(_make_input())
        assert "mn-tier-chip--bordered" in html

    def test_no_chips_ok(self):
        html = render_brand_bar_html(_make_input(chips=[]))
        assert 'class="mn-brand-bar"' in html
        assert "mn-tier-chip" not in html

    def test_xss_brand_escaped(self):
        html = render_brand_bar_html(_make_input(brand_text="<script>alert(1)</script>"))
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_brand_bar_html(_make_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-brand-bar" in html
        assert ".mn-tier-chip" in html


class TestRenderBrandBarCss:
    def test_uses_custom_properties(self):
        css = render_brand_bar_css()
        assert "var(--" in css
