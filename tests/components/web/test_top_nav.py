"""Tests fuer Web-Top-Nav-Renderer (UX-Welle v0.2, L1 Tier-Wechsel)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    TopNavInput,
    TopNavItem,
    WebTier,
)
from mn_design_system.components.web.top_nav import (
    render_top_nav_css,
    render_top_nav_html,
)


def _make_input(**overrides) -> TopNavInput:
    base = {
        "items": [
            TopNavItem(
                label="Start", href="/start/", tier=WebTier.START, active=True
            ),
            TopNavItem(
                label="Bibliothek", href="/bibliothek/", tier=WebTier.BIBLIOTHEK
            ),
            TopNavItem(label="Atelier", href="/atelier/", tier=WebTier.ATELIER),
            TopNavItem(label="Kabinett", href="/kabinett/", tier=WebTier.KABINETT),
        ],
    }
    base.update(overrides)
    return TopNavInput(**base)


class TestRenderTopNavHtml:
    def test_minimal_renders(self):
        html = render_top_nav_html(_make_input())
        assert 'class="mn-top-nav' in html
        assert "Start" in html

    def test_items_rendered(self):
        html = render_top_nav_html(_make_input())
        # Jedes <a> traegt mn-top-nav__item UND mn-top-nav__item--{tier} —
        # der Modifier-Praefix kommt genau 1x pro Eintrag (analog
        # test_tier_chip Punkt 6 / D1-Lehre: nicht den Basis-Substring zaehlen).
        assert html.count("mn-top-nav__item--") == 4
        assert "Bibliothek" in html
        assert "Atelier" in html
        assert "Kabinett" in html

    def test_active_item_marked(self):
        html = render_top_nav_html(_make_input())
        assert html.count("is-active") == 1

    def test_tier_modifier_per_item(self):
        html = render_top_nav_html(_make_input())
        for tier in ("start", "bibliothek", "atelier", "kabinett"):
            assert f"mn-top-nav__item--{tier}" in html

    def test_xss_label_escaped(self):
        html = render_top_nav_html(
            _make_input(
                items=[
                    TopNavItem(
                        label="<script>alert(1)</script>",
                        href="/x",
                        tier=WebTier.START,
                    )
                ]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_href_escaped(self):
        html = render_top_nav_html(
            _make_input(
                items=[
                    TopNavItem(
                        label="X",
                        href='/x"><script>alert(1)</script>',
                        tier=WebTier.START,
                    )
                ]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_top_nav_html(_make_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-top-nav" in html

    def test_nav_has_aria_label_default(self):
        """Spec §A6 / D1-Lehre: <nav> traegt ein aria-label — mehrere <nav>
        pro Seite (L1 Top-Nav + L3 Sub-Nav) muessen fuer Screenreader
        unterscheidbar sein (WCAG 2.4.1)."""
        html = render_top_nav_html(_make_input())
        assert 'aria-label="Hauptnavigation"' in html

    def test_nav_aria_label_overridable(self):
        html = render_top_nav_html(_make_input(aria_label="Bereichswechsel"))
        assert 'aria-label="Bereichswechsel"' in html

    def test_nav_aria_label_escaped(self):
        """aria_label ist ein Konsument-String — muss XSS-sicher escaped werden."""
        html = render_top_nav_html(
            _make_input(aria_label='"><script>alert(1)</script>')
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_active_item_has_aria_current(self):
        """D1-Lehre: aktiver Eintrag traegt aria-current="page" — die
        Aktiv-Information darf nicht rein visuell sein (WCAG)."""
        html = render_top_nav_html(_make_input())
        assert html.count('aria-current="page"') == 1


class TestRenderTopNavCss:
    def test_uses_tier_custom_properties(self):
        css = render_top_nav_css()
        for tier in ("bibliothek", "atelier", "kabinett", "start"):
            assert f"var(--color-tier-{tier}-bg" in css
            assert f"var(--color-tier-{tier}-text" in css

    def test_uses_dark_surface(self):
        """Spec §A4 L1: transparente Pills auf dunklem Grund."""
        css = render_top_nav_css()
        assert "var(--color-dark-surface" in css
