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
            _make_input(tabs=[SubNavTab(label="<script>alert(1)</script>", href="/x")])
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

    def test_nav_has_aria_label_default(self):
        """Spec §A6: <nav> traegt ein aria-label — mehrere <nav> pro Seite
        (L1 Top-Nav + L3 Sub-Nav) muessen fuer Screenreader unterscheidbar
        sein (WCAG 2.4.1). Default greift ohne explizites aria_label."""
        html = render_sub_nav_html(_make_input())
        assert 'aria-label="Bereichs-Navigation"' in html

    def test_nav_aria_label_overridable(self):
        html = render_sub_nav_html(_make_input(aria_label="Bibliothek-Bereiche"))
        assert 'aria-label="Bibliothek-Bereiche"' in html

    def test_nav_aria_label_escaped(self):
        """aria_label ist ein Konsument-String — muss XSS-sicher escaped werden."""
        html = render_sub_nav_html(
            _make_input(aria_label='"><script>alert(1)</script>')
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_active_tab_has_aria_current(self):
        """Spec §A6: aktiver Tab traegt aria-current="page" — die
        Aktiv-Information darf nicht rein visuell sein (WCAG)."""
        html = render_sub_nav_html(_make_input())
        assert html.count('aria-current="page"') == 1


class TestRenderSubNavCss:
    def test_css_hover_uses_bg_soft(self):
        css = render_sub_nav_css()
        assert "var(--color-tier-bibliothek-bg-soft" in css

    def test_css_active_uses_bg(self):
        css = render_sub_nav_css()
        assert "var(--color-tier-bibliothek-bg" in css

    def test_tab_has_focus_visible(self):
        """A2 welle-weit: jeder Sub-Nav-Tab hat einen sichtbaren,
        Token-basierten :focus-visible-Indikator (WCAG 2.4.7) — die Sub-Nav
        ist tastaturbedienbar. Foundation: Fokus-Ring aus web.stroke/web.color."""
        css = render_sub_nav_css()
        assert ".mn-sub-nav__tab:focus-visible" in css
        assert "outline" in css
        assert "var(--web-stroke-focus" in css
        assert "var(--web-color-focus-ring" in css

    def test_css_uses_foundation_tokens(self):
        """Re-Tokenisierung: Stroke, Schriftgroesse und Schriftfamilie kommen
        aus der Web-Foundation, nicht mehr aus ad-hoc rem/Print-Tokens."""
        css = render_sub_nav_css()
        assert "var(--web-stroke-line" in css
        assert "var(--web-color-separator" in css
        assert "var(--web-text-ui" in css
        assert "var(--web-font-sans" in css
        assert "var(--web-layout-content-width" in css
        assert "var(--web-layout-page-inset" in css

    def test_css_no_print_pt_units(self):
        """Keine pt-Einheiten — die Sub-Nav ist rein web."""
        css = render_sub_nav_css()
        assert "pt" not in css
