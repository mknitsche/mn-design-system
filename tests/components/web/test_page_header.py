"""Tests fuer Web-Page-Header-Renderer (UX-Welle v0.2)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import PageHeaderInput
from mn_design_system.components.web.page_header import (
    render_page_header_css,
    render_page_header_html,
)


class TestRenderPageHeaderHtml:
    def test_minimal_renders(self):
        html = render_page_header_html(PageHeaderInput(title="Bibliothek"))
        assert 'class="mn-page-header' in html
        assert "<h1" in html
        assert "Bibliothek" in html

    def test_uses_header_element(self):
        """Semantisches HTML: Seiten-Kopf ist ein <header>."""
        html = render_page_header_html(PageHeaderInput(title="X"))
        assert "<header" in html
        assert "</header>" in html

    def test_lead_when_provided(self):
        html = render_page_header_html(
            PageHeaderInput(title="Atelier", lead="Werkstatt fuer Entwuerfe.")
        )
        assert "mn-page-header__lead" in html
        assert "Werkstatt fuer Entwuerfe." in html

    def test_lead_omitted_when_none(self):
        html = render_page_header_html(PageHeaderInput(title="Atelier"))
        assert "mn-page-header__lead" not in html

    def test_xss_title_escaped(self):
        html = render_page_header_html(
            PageHeaderInput(title="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_lead_escaped(self):
        html = render_page_header_html(
            PageHeaderInput(title="X", lead="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_page_header_html(PageHeaderInput(title="X"), inline_css=True)
        assert "<style>" in html
        assert ".mn-page-header" in html


class TestRenderPageHeaderCss:
    def test_uses_custom_properties(self):
        css = render_page_header_css()
        assert "var(--color-light-h1" in css
        assert "var(--color-light-text-muted" in css
