"""Tests fuer den Web-News-Item-Renderer (Briefing-Web, Welle 3).

News-Item = Kaskaden-Einheit: Rang + Titel (optional "tiefer"-Link) + Basis-Text
+ Meta-Zeile (Kategorie · Zeit · Quelle) + optionaler "+ mehr"-Expander. Der
Aufmacher ist dezent prominent (Top-Akzentlinie + groesserer Titel).
"""

from __future__ import annotations

import re

from mn_design_system.components._patterns.contracts import (
    NewsItemDetail,
    NewsItemInput,
    SourceLink,
    SourceRefInput,
)
from mn_design_system.components.web.news_item import (
    render_news_item_css,
    render_news_item_html,
)

# Hex nur als var()-Fallback erlaubt — d.h. unmittelbar von ", " vorangestellt.
_HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def _source(label: str = "euronews.com") -> SourceRefInput:
    return SourceRefInput(primary=SourceLink(href="/x", label=label))


def _make_item(**overrides) -> NewsItemInput:
    base = {
        "title": "EU-Kommission warnt vor Abhaengigkeit",
        "text": "Bruessel reagiert auf den US-Exklusivzugang.",
        "kategorie": "Politik",
        "zeitangabe": "vor 3 Std",
    }
    base.update(overrides)
    return NewsItemInput(**base)


class TestRenderNewsItemHtml:
    def test_minimal_renders(self):
        html = render_news_item_html(_make_item())
        assert '<article class="mn-news-item' in html
        assert "mn-news-item__row" in html
        assert "mn-news-item__body" in html
        assert "EU-Kommission warnt vor Abhaengigkeit" in html
        assert "Bruessel reagiert auf den US-Exklusivzugang." in html
        assert "</article>" in html

    def test_uses_article_and_h3(self):
        html = render_news_item_html(_make_item())
        assert "<article" in html
        assert '<h3 class="mn-news-item__title">' in html

    def test_meta_line_has_kategorie_and_zeit(self):
        html = render_news_item_html(_make_item())
        assert 'class="mn-news-item__cat">Politik' in html
        assert "vor 3 Std" in html

    def test_rank_rendered_when_set(self):
        html = render_news_item_html(_make_item(rank="01"))
        assert 'class="mn-news-item__rank">01' in html

    def test_rank_omitted_when_none(self):
        html = render_news_item_html(_make_item())
        assert "mn-news-item__rank" not in html

    def test_eyebrow_rendered_when_set(self):
        html = render_news_item_html(_make_item(eyebrow="Aufmacher · stand auf S1"))
        assert 'class="mn-news-item__eyebrow">Aufmacher · stand auf S1' in html

    def test_eyebrow_omitted_when_none(self):
        html = render_news_item_html(_make_item())
        assert "mn-news-item__eyebrow" not in html

    def test_deeper_href_makes_title_a_link(self):
        html = render_news_item_html(_make_item(deeper_href="#fin-aufmacher"))
        assert 'class="mn-news-item__title-link"' in html
        assert 'href="#fin-aufmacher"' in html

    def test_no_deeper_href_title_is_plain(self):
        html = render_news_item_html(_make_item())
        assert "mn-news-item__title-link" not in html
        assert "<a " not in html

    def test_is_aufmacher_adds_modifier(self):
        html = render_news_item_html(_make_item(is_aufmacher=True))
        assert "mn-news-item--aufmacher" in html

    def test_not_aufmacher_no_modifier(self):
        html = render_news_item_html(_make_item())
        assert "mn-news-item--aufmacher" not in html

    def test_source_embeds_source_ref(self):
        html = render_news_item_html(_make_item(source=_source("euronews.com")))
        assert "mn-source-ref" in html
        assert "Quelle: " in html
        assert "euronews.com" in html

    def test_no_source_no_source_ref_in_meta(self):
        html = render_news_item_html(_make_item())
        # Ohne detail.sources darf nirgends ein source-ref auftauchen.
        assert "mn-source-ref" not in html

    def test_detail_none_no_details(self):
        html = render_news_item_html(_make_item())
        assert "<details" not in html

    def test_detail_renders_expander(self):
        html = render_news_item_html(
            _make_item(
                detail=NewsItemDetail(
                    level_label="Medium · Lagebericht",
                    text="Die Kommission prueft eine Reaktion.",
                    summary_label="medium",
                )
            )
        )
        assert '<details class="mn-news-item__details">' in html
        assert "+ mehr (medium)" in html
        assert 'class="mn-news-item__level">Medium · Lagebericht' in html
        assert "Die Kommission prueft eine Reaktion." in html

    def test_detail_sources_embed_source_ref(self):
        html = render_news_item_html(
            _make_item(
                detail=NewsItemDetail(
                    level_label="Detailliert",
                    text="Mehr.",
                    sources=SourceRefInput(
                        primary=SourceLink(href="/a", label="euronews.com"),
                        weitere=[SourceLink(href="/b", label="heise.de")],
                    ),
                )
            )
        )
        assert "mn-source-ref" in html
        assert "weitere:" in html
        assert "heise.de" in html

    def test_detail_default_summary_label(self):
        html = render_news_item_html(
            _make_item(detail=NewsItemDetail(level_label="L", text="x"))
        )
        assert "+ mehr (mehr)" in html

    def test_xss_title_escaped(self):
        html = render_news_item_html(_make_item(title="<script>alert(1)</script>"))
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_text_escaped(self):
        html = render_news_item_html(_make_item(text="<script>alert(1)</script>"))
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_deeper_href_escaped(self):
        html = render_news_item_html(
            _make_item(deeper_href='/x"><script>alert(1)</script>')
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_detail_text_escaped(self):
        html = render_news_item_html(
            _make_item(
                detail=NewsItemDetail(level_label="L", text="<script>alert(1)</script>")
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_inline_css_embedded(self):
        html = render_news_item_html(_make_item(), inline_css=True)
        assert "<style>" in html
        assert ".mn-news-item" in html
        # inline_css zieht das eingebettete Source-Ref-CSS mit.
        assert ".mn-source-ref" in html


class TestRenderNewsItemCss:
    def test_returns_css(self):
        css = render_news_item_css()
        assert ".mn-news-item {" in css

    def test_carries_structural_classes(self):
        css = render_news_item_css()
        for cls in (
            ".mn-news-item__row",
            ".mn-news-item__rank",
            ".mn-news-item__body",
            ".mn-news-item__eyebrow",
            ".mn-news-item__title",
            ".mn-news-item__text",
            ".mn-news-item__meta",
            ".mn-news-item__cat",
            ".mn-news-item__detail",
            ".mn-news-item__level",
            ".mn-news-item__more",
        ):
            assert cls in css

    def test_aufmacher_modifier_present(self):
        css = render_news_item_css()
        assert ".mn-news-item--aufmacher {" in css
        # Top-Akzentlinie + groesserer Titel.
        assert "border-top:" in css
        assert ".mn-news-item--aufmacher .mn-news-item__title {" in css

    def test_uses_foundation_tokens(self):
        css = render_news_item_css()
        assert "var(--web-text-lead" in css
        assert "var(--web-text-body" in css
        assert "var(--web-font-sans" in css
        assert "var(--space-" in css
        assert "var(--web-stroke-line" in css

    def test_title_color_and_text_color_tokens(self):
        css = render_news_item_css()
        assert "var(--color-light-h1" in css
        assert "var(--color-grey-700" in css

    def test_title_link_focus_visible(self):
        css = render_news_item_css()
        assert ".mn-news-item__title-link:focus-visible" in css
        assert "var(--web-stroke-focus" in css
        assert "var(--web-color-focus-ring" in css

    def test_details_marker_hidden(self):
        """Native Disclosure-Marker ausgeblendet (eigener Summary-Stil)."""
        css = render_news_item_css()
        assert "list-style: none" in css
        assert "::-webkit-details-marker" in css

    def test_no_print_pt_units(self):
        """Keine pt-Einheiten — rein web. Geprueft auf pt als Einheit
        ('pt;' / 'pt '); der Token-Schritt 'caption' enthaelt 'pt' legitim."""
        css = render_news_item_css()
        assert "pt;" not in css and "pt " not in css

    def test_no_naked_hex_only_fallbacks(self):
        """Jeder Hex-Wert steht ausschliesslich als var()-Fallback (", #…")."""
        css = render_news_item_css()
        for match in _HEX.finditer(css):
            preceding = css[max(0, match.start() - 2) : match.start()]
            assert preceding == ", ", (
                f"Nackter Hex {match.group()}: '{css[match.start() - 15 : match.start() + 8]}'"
            )
