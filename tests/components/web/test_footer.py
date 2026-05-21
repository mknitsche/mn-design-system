"""Tests fuer Web-Footer-Renderer — schlanke Schlusszeile (cld1-S21).

Footer = einzeilige Seiten-Fusszeile: links `|`-getrennte Identitaets-Segmente,
rechts `·`-getrennte Rechtslinks + optionale Version.
"""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import (
    FooterInput,
    FooterLink,
    FooterSegment,
)
from mn_design_system.components.web.footer import (
    render_footer_css,
    render_footer_html,
)


def _make_input(**overrides) -> FooterInput:
    base = {
        "segments": [
            FooterSegment(text="mkn-desk.com"),
            FooterSegment(text="Atelier · AMBER"),
            FooterSegment(text="Profil …", slot_id="footer-user-info"),
        ],
        "links": [
            FooterLink(label="Impressum", href="/impressum"),
            FooterLink(label="Datenschutz", href="/datenschutz"),
        ],
    }
    base.update(overrides)
    return FooterInput(**base)


class TestRenderFooterHtml:
    def test_minimal_renders(self):
        html = render_footer_html(_make_input())
        assert 'class="mn-footer"' in html

    def test_uses_footer_element(self):
        """Semantisches HTML: Seiten-Fuss ist ein <footer>."""
        html = render_footer_html(_make_input())
        assert "<footer" in html
        assert "</footer>" in html

    def test_inner_structure(self):
        """Eine Zeile: Identitaet links + Meta rechts in einem flex-inner."""
        html = render_footer_html(_make_input())
        assert "mn-footer__inner" in html
        assert "mn-footer__identity" in html
        assert "mn-footer__meta" in html

    def test_segments_rendered(self):
        html = render_footer_html(_make_input())
        assert "mkn-desk.com" in html
        assert "Atelier · AMBER" in html
        assert "Profil" in html

    def test_segments_separated_by_pipe(self):
        """Drei Identitaets-Segmente → zwei |-Striche dazwischen."""
        html = render_footer_html(_make_input())
        assert html.count('mn-footer__sep" aria-hidden="true">|') == 2

    def test_slot_segment_carries_id(self):
        """Ein Segment mit slot_id wird zum Hydration-Slot mit id-Attribut."""
        html = render_footer_html(_make_input())
        assert 'id="footer-user-info"' in html
        assert "mn-footer__slot" in html

    def test_plain_segment_has_no_slot(self):
        html = render_footer_html(
            _make_input(segments=[FooterSegment(text="mkn-desk.com")])
        )
        assert "mn-footer__seg" in html
        assert "mn-footer__slot" not in html

    def test_links_rendered(self):
        html = render_footer_html(_make_input())
        assert "Impressum" in html
        assert 'href="/impressum"' in html
        assert "Datenschutz" in html

    def test_links_separated_by_middot(self):
        """Zwei Links + Version → zwei ·-Trenner im rechten Cluster."""
        html = render_footer_html(_make_input(version="v0.2.1"))
        assert html.count('mn-footer__sep" aria-hidden="true">·') == 2

    def test_version_when_provided(self):
        html = render_footer_html(_make_input(version="v0.2.1"))
        assert "v0.2.1" in html
        assert "mn-footer__version" in html

    def test_version_omitted_when_none(self):
        html = render_footer_html(_make_input())
        assert "mn-footer__version" not in html

    def test_inline_css_embedded(self):
        html = render_footer_html(_make_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-footer" in html

    def test_xss_segment_text_escaped(self):
        html = render_footer_html(
            _make_input(segments=[FooterSegment(text="<script>alert(1)</script>")])
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_slot_id_escaped(self):
        html = render_footer_html(
            _make_input(
                segments=[
                    FooterSegment(text="P", slot_id='x"><script>alert(1)</script>')
                ]
            )
        )
        assert "<script>" not in html

    def test_xss_link_label_escaped(self):
        html = render_footer_html(
            _make_input(
                links=[FooterLink(label="<script>alert(1)</script>", href="/x")]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_link_href_escaped(self):
        html = render_footer_html(
            _make_input(
                links=[FooterLink(label="X", href='/x"><script>alert(1)</script>')]
            )
        )
        assert "<script>" not in html

    def test_xss_version_escaped(self):
        html = render_footer_html(_make_input(version="<script>alert(1)</script>"))
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestRenderFooterCss:
    def test_uses_custom_properties(self):
        css = render_footer_css()
        assert "var(--web-color-separator" in css
        assert "var(--color-light-text" in css

    def test_uses_foundation_tokens(self):
        """Re-Tokenisierung: Stroke, Schriftgroesse, Schriftfamilie, Inhalts-
        Breite und Seiten-Einzug kommen aus der Web-Foundation."""
        css = render_footer_css()
        assert "var(--web-stroke-line" in css
        assert "var(--web-text-ui" in css
        assert "var(--web-font-sans" in css
        assert "var(--web-layout-content-width" in css
        assert "var(--web-layout-page-inset" in css

    def test_no_print_pt_units(self):
        """Der Footer trug die einzige print-Linie (stroke.thin 0.5pt) — nach
        der Re-Tokenisierung ist der Footer rein web, keine pt-Einheit mehr."""
        css = render_footer_css()
        assert "pt" not in css

    def test_link_has_focus_visible(self):
        """Footer-Links haben einen sichtbaren, Token-basierten
        :focus-visible-Indikator (WCAG 2.4.7) — Foundation-Fokus-Ring."""
        css = render_footer_css()
        assert ".mn-footer__link:focus-visible" in css
        assert "outline" in css
        assert "var(--web-stroke-focus" in css
        assert "var(--web-color-focus-ring" in css

    def test_hochstrich_border_top(self):
        """Die Hochstrich-Trennlinie ist ein border-top am <footer>."""
        css = render_footer_css()
        assert ".mn-footer {" in css
        assert "border-top:" in css
