"""Tests fuer Web-Sub-Nav-Renderer (UX-Welle v0.2, L3 Auswahl)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    SubNavInput,
    SubNavTab,
    WebTier,
)
from mn_design_system.components.web.sub_nav import (
    render_sub_nav_css,
    render_sub_nav_html,
)


def _make_input(**overrides) -> SubNavInput:
    base = {
        "tier": WebTier.BIBLIOTHEK,
        "tabs": [
            SubNavTab(label="Alle", href="/bibliothek/", active=True),
            SubNavTab(label="Buecher", href="/bibliothek/buecher"),
            SubNavTab(label="Notizen", href="/bibliothek/notizen"),
        ],
    }
    base.update(overrides)
    return SubNavInput(**base)


class TestRenderSubNavHtml:
    def test_minimal_renders(self):
        html = render_sub_nav_html(_make_input())
        assert 'class="mn-sub-nav' in html
        assert "Alle" in html

    def test_tabs_rendered(self):
        html = render_sub_nav_html(_make_input())
        assert html.count("mn-sub-nav__tab") == 3
        assert "Buecher" in html
        assert "Notizen" in html

    def test_active_tab_marked(self):
        html = render_sub_nav_html(_make_input())
        assert html.count("is-active") == 1

    def test_tier_modifier_class(self):
        html = render_sub_nav_html(_make_input(tier=WebTier.ATELIER))
        assert "mn-sub-nav--atelier" in html

    def test_xss_label_escaped(self):
        html = render_sub_nav_html(
            _make_input(
                tabs=[SubNavTab(label="<script>alert(1)</script>", href="/x")]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_href_escaped(self):
        html = render_sub_nav_html(
            _make_input(
                tabs=[SubNavTab(label="X", href='/x"><script>alert(1)</script>')]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_sub_nav_html(_make_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-sub-nav" in html


class TestRenderSubNavCss:
    def test_css_hover_uses_bg_soft(self):
        css = render_sub_nav_css()
        assert "var(--color-tier-bibliothek-bg-soft" in css

    def test_css_active_uses_bg(self):
        css = render_sub_nav_css()
        assert "var(--color-tier-bibliothek-bg" in css
