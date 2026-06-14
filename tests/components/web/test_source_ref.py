"""Tests fuer den Web-Source-Ref-Renderer (Briefing-Web, Welle 3).

Source-Ref = "Quelle erstklassig": "Quelle: <a>label ↗</a>" + optional
"· weitere: <a>… ↗</a> · …". Kleine graue Meta-Optik.
"""

from __future__ import annotations

import re

from mn_design_system.components._patterns.contracts import (
    SourceLink,
    SourceRefInput,
)
from mn_design_system.components.web.source_ref import (
    render_source_ref_css,
    render_source_ref_html,
)

# Hex nur als var()-Fallback erlaubt — d.h. unmittelbar von ", " vorangestellt.
_HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def _link(
    label: str = "euronews.com", href: str = "https://euronews.com"
) -> SourceLink:
    return SourceLink(href=href, label=label)


class TestRenderSourceRefHtml:
    def test_minimal_renders_primary(self):
        html = render_source_ref_html(SourceRefInput(primary=_link()))
        assert '<span class="mn-source-ref">' in html
        assert "Quelle: " in html
        assert "euronews.com" in html
        assert 'href="https://euronews.com"' in html
        assert "</span>" in html

    def test_primary_uses_link_class(self):
        html = render_source_ref_html(SourceRefInput(primary=_link()))
        assert 'class="mn-source-ref__link"' in html

    def test_no_weitere_omits_weitere_label(self):
        html = render_source_ref_html(SourceRefInput(primary=_link()))
        assert "weitere:" not in html

    def test_weitere_rendered(self):
        html = render_source_ref_html(
            SourceRefInput(
                primary=_link("a", "/a"),
                weitere=[_link("b", "/b"), _link("c", "/c")],
            )
        )
        assert "· weitere: " in html
        assert "/b" in html
        assert "/c" in html
        # Primary + 2 weitere = 3 Links.
        assert html.count('class="mn-source-ref__link"') == 3

    def test_weitere_separated_by_middot(self):
        """Zwei weitere Quellen → genau ein ·-Trenner zwischen ihnen."""
        html = render_source_ref_html(
            SourceRefInput(
                primary=_link("a", "/a"),
                weitere=[_link("b", "/b"), _link("c", "/c")],
            )
        )
        # "· weitere: b · c" → der Trenner zwischen b und c ist ein weiteres "·".
        assert " · weitere: " in html
        weitere_teil = html.split("· weitere:")[1]
        assert weitere_teil.count(" · ") == 1

    def test_inline_css_embedded(self):
        html = render_source_ref_html(SourceRefInput(primary=_link()), inline_css=True)
        assert "<style>" in html
        assert ".mn-source-ref" in html

    def test_xss_label_escaped(self):
        html = render_source_ref_html(
            SourceRefInput(primary=_link(label="<script>alert(1)</script>"))
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_href_escaped(self):
        html = render_source_ref_html(
            SourceRefInput(primary=_link(href='/x"><script>alert(1)</script>'))
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestRenderSourceRefCss:
    def test_returns_css(self):
        css = render_source_ref_css()
        assert ".mn-source-ref {" in css

    def test_link_class_present(self):
        css = render_source_ref_css()
        assert ".mn-source-ref__link" in css

    def test_external_arrow_via_css(self):
        """Der ↗-Pfeil kommt per ::after (Inhalt/Dekoration getrennt)."""
        css = render_source_ref_css()
        assert ".mn-source-ref__link::after" in css
        assert "\\2197" in css

    def test_uses_foundation_tokens(self):
        css = render_source_ref_css()
        assert "var(--web-text-caption" in css
        assert "var(--color-light-text-muted" in css

    def test_link_has_focus_visible(self):
        css = render_source_ref_css()
        assert ".mn-source-ref__link:focus-visible" in css
        assert "var(--web-stroke-focus" in css
        assert "var(--web-color-focus-ring" in css

    def test_no_print_pt_units(self):
        """Keine pt-Einheiten — rein web. Geprueft auf pt als Einheit
        ('pt;' / 'pt '); der Token-Schritt 'caption' enthaelt 'pt' legitim."""
        css = render_source_ref_css()
        assert "pt;" not in css and "pt " not in css

    def test_no_naked_hex_only_fallbacks(self):
        """Jeder Hex-Wert steht ausschliesslich als var()-Fallback (", #…")."""
        css = render_source_ref_css()
        for match in _HEX.finditer(css):
            preceding = css[max(0, match.start() - 2) : match.start()]
            assert preceding == ", ", (
                f"Nackter Hex {match.group()}: '{css[match.start() - 15 : match.start() + 8]}'"
            )
