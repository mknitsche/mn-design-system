"""Tests fuer Web-Footer-Renderer (UX-Welle v0.2, 3-Block + Version)."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    FooterColumn,
    FooterInput,
    FooterLink,
)
from mn_design_system.components.web.footer import (
    render_footer_css,
    render_footer_html,
)
from mn_design_system.tokens import get


def _make_input(**overrides) -> FooterInput:
    base = {
        "columns": [
            FooterColumn(
                title="Bereiche",
                links=[
                    FooterLink(label="Start", href="/start/"),
                    FooterLink(label="Bibliothek", href="/bibliothek/"),
                ],
            ),
            FooterColumn(
                title="Rechtliches",
                links=[
                    FooterLink(label="Impressum", href="/impressum"),
                    FooterLink(label="Datenschutz", href="/datenschutz"),
                ],
            ),
            FooterColumn(
                title="Kontakt",
                links=[FooterLink(label="E-Mail", href="mailto:x@y.de")],
            ),
        ],
    }
    base.update(overrides)
    return FooterInput(**base)


class TestRenderFooterHtml:
    def test_minimal_renders(self):
        html = render_footer_html(_make_input())
        assert 'class="mn-footer' in html

    def test_uses_footer_element(self):
        """Semantisches HTML: Seiten-Fuss ist ein <footer>."""
        html = render_footer_html(_make_input())
        assert "<footer" in html
        assert "</footer>" in html

    def test_columns_rendered(self):
        html = render_footer_html(_make_input())
        assert html.count("mn-footer__col-title") == 3
        assert "Bereiche" in html
        assert "Rechtliches" in html
        assert "Kontakt" in html

    def test_links_rendered(self):
        html = render_footer_html(_make_input())
        assert "Impressum" in html
        assert "Datenschutz" in html
        assert 'href="/impressum"' in html

    def test_version_when_provided(self):
        html = render_footer_html(_make_input(version="v0.2.0"))
        assert "v0.2.0" in html
        assert "mn-footer__meta" in html

    def test_version_omitted_when_none(self):
        html = render_footer_html(_make_input())
        assert "v0.2.0" not in html

    def test_note_when_provided(self):
        html = render_footer_html(_make_input(note="© 2026 MN"))
        assert "© 2026 MN" in html
        assert "mn-footer__meta" in html

    def test_note_omitted_when_none(self):
        html = render_footer_html(_make_input())
        assert "mn-footer__meta" not in html

    def test_xss_link_label_escaped(self):
        html = render_footer_html(
            _make_input(
                columns=[
                    FooterColumn(
                        title="X",
                        links=[
                            FooterLink(
                                label="<script>alert(1)</script>", href="/x"
                            )
                        ],
                    )
                ]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_href_escaped(self):
        html = render_footer_html(
            _make_input(
                columns=[
                    FooterColumn(
                        title="X",
                        links=[
                            FooterLink(
                                label="X",
                                href='/x"><script>alert(1)</script>',
                            )
                        ],
                    )
                ]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_col_title_escaped(self):
        html = render_footer_html(
            _make_input(
                columns=[
                    FooterColumn(
                        title="<script>alert(1)</script>",
                        links=[FooterLink(label="X", href="/x")],
                    )
                ]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_version_escaped(self):
        html = render_footer_html(
            _make_input(version="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_note_escaped(self):
        html = render_footer_html(
            _make_input(note="<script>alert(1)</script>")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_footer_html(_make_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-footer" in html

    def test_user_info_slot_rendered_when_id_set(self):
        html = render_footer_html(
            _make_input(user_info_id="footer-user-info")
        )
        assert 'id="footer-user-info"' in html
        assert "mn-footer__meta" in html

    def test_no_user_info_slot_when_id_none(self):
        html = render_footer_html(_make_input())
        assert 'id="footer-user-info"' not in html

    def test_user_info_label_rendered_in_slot(self):
        html = render_footer_html(
            _make_input(
                user_info_id="footer-user-info",
                user_info_label="lade …",
            )
        )
        assert "lade …" in html

    def test_xss_user_info_id_escaped(self):
        html = render_footer_html(
            _make_input(user_info_id='x"><script>alert(1)</script>')
        )
        assert "<script>" not in html

    def test_xss_user_info_label_escaped(self):
        html = render_footer_html(
            _make_input(
                user_info_id="footer-user-info",
                user_info_label="<script>alert(1)</script>",
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestRenderFooterCss:
    def test_uses_custom_properties(self):
        css = render_footer_css()
        assert "var(--color-light-border" in css
        assert "var(--color-light-text" in css

    def test_stroke_thin_fallback_matches_token_unit(self):
        """Befund 3 (A2-D2): der var()-Fallback fuer stroke.thin muss in Wert
        UND Einheit dem Token entsprechen (0.5pt, nicht 0.5px — pt und px
        sind verschiedene Einheiten)."""
        css = render_footer_css()
        soll = get("stroke.thin")
        assert soll == "0.5pt"
        assert f"var(--stroke-thin, {soll})" in css

    def test_link_has_focus_visible(self):
        """A2 welle-weit: Footer-Links haben einen sichtbaren, Token-basierten
        :focus-visible-Indikator (WCAG 2.4.7)."""
        css = render_footer_css()
        assert ".mn-footer__link:focus-visible" in css
        assert "outline" in css
        assert "var(--color-light-accent" in css
