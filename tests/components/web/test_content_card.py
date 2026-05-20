"""Tests fuer Web-Content-Card- und Card-Grid-Renderer (UX-Welle v0.2)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    CardGridInput,
    ContentCardInput,
    WebTier,
)
from mn_design_system.components.web.content_card import (
    render_card_grid_css,
    render_card_grid_html,
    render_content_card_css,
    render_content_card_html,
)


def _make_card(**overrides) -> ContentCardInput:
    base = {
        "title": "Reisefotografie",
        "body": "Eine Auswahl aus zehn Jahren unterwegs.",
    }
    base.update(overrides)
    return ContentCardInput(**base)


def _make_grid(**overrides) -> CardGridInput:
    base = {
        "cards": [
            ContentCardInput(title="Karte A", body="Inhalt A"),
            ContentCardInput(title="Karte B", body="Inhalt B"),
            ContentCardInput(title="Karte C", body="Inhalt C"),
        ],
    }
    base.update(overrides)
    return CardGridInput(**base)


class TestRenderContentCardHtml:
    def test_card_minimal_renders(self):
        html = render_content_card_html(_make_card())
        assert '<article class="mn-content-card' in html
        assert "Reisefotografie" in html
        assert "Eine Auswahl aus zehn Jahren unterwegs." in html
        assert "</article>" in html

    def test_card_without_href_no_link(self):
        html = render_content_card_html(_make_card())
        assert "<a " not in html

    def test_card_with_href(self):
        html = render_content_card_html(_make_card(href="/atelier/reise/"))
        assert 'href="/atelier/reise/"' in html
        assert "<a " in html

    def test_card_with_tier(self):
        html = render_content_card_html(_make_card(tier=WebTier.KABINETT))
        assert "mn-content-card--kabinett" in html

    def test_card_without_tier_no_modifier(self):
        html = render_content_card_html(_make_card())
        assert "mn-content-card--" not in html

    def test_xss_title_escaped(self):
        html = render_content_card_html(
            _make_card(title="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_body_escaped(self):
        html = render_content_card_html(
            _make_card(body="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_href_escaped(self):
        html = render_content_card_html(
            _make_card(href='/x"><script>alert(1)</script>')
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_content_card_html(_make_card(), inline_css=True)
        assert "<style>" in html
        assert ".mn-content-card" in html


class TestRenderContentCardCss:
    def test_returns_css(self):
        css = render_content_card_css()
        assert ".mn-content-card {" in css

    def test_uses_css_custom_properties(self):
        css = render_content_card_css()
        assert "var(--color-light-border" in css
        assert "var(--color-light-h1" in css

    def test_tier_modifier_uses_border_token(self):
        css = render_content_card_css()
        for tier in ("bibliothek", "atelier", "kabinett", "start"):
            assert f"var(--color-tier-{tier}-border" in css

    def test_cursor_pointer_only_for_linked_card(self):
        """Carry-over D1/D2: cursor:pointer nur fuer die verlinkte Card."""
        css = render_content_card_css()
        assert "cursor: pointer" in css


class TestRenderCardGridHtml:
    def test_grid_renders_all_cards(self):
        html = render_card_grid_html(_make_grid())
        assert html.count("mn-content-card--") == 0
        assert html.count('<article class="mn-content-card') == 3
        assert "Karte A" in html
        assert "Karte B" in html
        assert "Karte C" in html

    def test_grid_wrapper_class(self):
        html = render_card_grid_html(_make_grid())
        assert 'class="mn-card-grid"' in html

    def test_grid_columns_css_var_default(self):
        html = render_card_grid_html(_make_grid())
        assert "--mn-card-grid-cols:3" in html

    def test_grid_columns_css_var(self):
        html = render_card_grid_html(_make_grid(columns=2))
        assert "--mn-card-grid-cols:2" in html

    def test_grid_embeds_tier_card(self):
        grid = _make_grid(
            cards=[ContentCardInput(title="T", body="B", tier=WebTier.ATELIER)]
        )
        html = render_card_grid_html(grid)
        assert "mn-content-card--atelier" in html

    def test_xss_card_title_escaped_in_grid(self):
        grid = _make_grid(
            cards=[ContentCardInput(title="<script>x</script>", body="B")]
        )
        html = render_card_grid_html(grid)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_card_grid_html(_make_grid(), inline_css=True)
        assert "<style>" in html
        assert ".mn-card-grid" in html
        assert ".mn-content-card" in html


class TestRenderCardGridCss:
    def test_returns_css(self):
        css = render_card_grid_css()
        assert ".mn-card-grid {" in css

    def test_grid_uses_columns_variable(self):
        css = render_card_grid_css()
        assert "var(--mn-card-grid-cols" in css
