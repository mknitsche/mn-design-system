"""Tests fuer Web-Tier-Chip-Renderer (UX-Welle v0.2)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import TierChipInput, WebTier
from mn_design_system.components.web.tier_chip import (
    render_tier_chip_css,
    render_tier_chip_html,
)


class TestRenderTierChipHtml:
    def test_minimal_renders(self):
        html = render_tier_chip_html(TierChipInput(tier=WebTier.BIBLIOTHEK, label="Bibliothek"))
        assert 'class="mn-tier-chip' in html
        assert "mn-tier-chip--bibliothek" in html
        assert "Bibliothek" in html

    def test_bordered_default(self):
        html = render_tier_chip_html(TierChipInput(tier=WebTier.ATELIER, label="Atelier"))
        assert "mn-tier-chip--bordered" in html

    def test_borderless_variant(self):
        html = render_tier_chip_html(
            TierChipInput(tier=WebTier.KABINETT, label="Kabinett", bordered=False)
        )
        assert "mn-tier-chip--bordered" not in html

    def test_xss_label_escaped(self):
        html = render_tier_chip_html(
            TierChipInput(tier=WebTier.START, label="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_tier_chip_html(
            TierChipInput(tier=WebTier.BIBLIOTHEK, label="X"), inline_css=True
        )
        assert "<style>" in html
        assert ".mn-tier-chip" in html


class TestRenderTierChipCss:
    def test_uses_tier_custom_properties(self):
        css = render_tier_chip_css()
        for tier in ("bibliothek", "atelier", "kabinett", "start"):
            assert f"var(--color-tier-{tier}-bg" in css
            assert f"var(--color-tier-{tier}-text" in css

    def test_bordered_uses_border_token(self):
        css = render_tier_chip_css()
        assert "var(--color-tier-bibliothek-border" in css
