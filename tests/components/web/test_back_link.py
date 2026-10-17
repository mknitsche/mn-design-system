"""Tests fuer die Web-Zurueck-Zeile (0.19.0, claudeAI TODO-885 Ordnung 2)."""

from __future__ import annotations

import re

import pydantic
import pytest

from mn_design_system.components._patterns.contracts import BackLinkInput
from mn_design_system.components.web import (
    render_back_link_css,
    render_back_link_html,
)


class TestBackLinkInput:
    def test_href_und_label_pflicht(self):
        with pytest.raises(pydantic.ValidationError):
            BackLinkInput(href="", label="Briefing")
        with pytest.raises(pydantic.ValidationError):
            BackLinkInput(href="/bibliothek/briefing/", label="")

    def test_frozen_und_extra_verboten(self):
        eingabe = BackLinkInput(href="/x/", label="X")
        with pytest.raises(pydantic.ValidationError):
            eingabe.label = "Y"
        with pytest.raises(pydantic.ValidationError):
            BackLinkInput(href="/x/", label="X", extra="nein")


class TestRenderBackLinkHtml:
    def test_struktur(self):
        html = render_back_link_html(
            BackLinkInput(href="/bibliothek/briefing/", label="Briefing")
        )
        assert html.startswith('<nav class="mn-back-link" aria-label="Zurück">')
        assert '<a href="/bibliothek/briefing/">' in html
        assert html.endswith("</a></nav>")
        assert "Briefing" in html

    def test_pfeil_ist_fuer_screenreader_versteckt(self):
        html = render_back_link_html(BackLinkInput(href="/x/", label="Wissen"))
        assert '<span aria-hidden="true">←</span> Wissen' in html

    def test_genau_ein_link(self):
        html = render_back_link_html(BackLinkInput(href="/x/", label="Wissen"))
        assert html.count("<a ") == 1
        assert html.count("<nav") == 1

    def test_href_und_label_werden_escaped(self):
        html = render_back_link_html(
            BackLinkInput(href='/x/"><script>1</script>', label="<b>X</b> & Y")
        )
        assert "<script>" not in html
        assert "<b>" not in html
        assert "&lt;b&gt;X&lt;/b&gt; &amp; Y" in html
        assert '"><script' not in html

    def test_inline_css_haengt_style_an(self):
        html = render_back_link_html(
            BackLinkInput(href="/x/", label="X"), inline_css=True
        )
        assert html.startswith("<style>")
        assert ".mn-back-link" in html

    def test_ohne_inline_css_kein_style(self):
        html = render_back_link_html(BackLinkInput(href="/x/", label="X"))
        assert "<style" not in html


class TestRenderBackLinkCss:
    def test_klasse_vorhanden(self):
        assert ".mn-back-link" in render_back_link_css()

    def test_keine_literalfarbe_ausserhalb_von_var(self):
        css = render_back_link_css()
        # jede Farbe steht als var(--…, <Rueckfall>); ausserhalb von var() kein Hex
        ohne_var = re.sub(r"var\([^;]*\)", "", css)
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var)
        assert "rgb" not in ohne_var

    def test_touch_ziel_hover_und_fokus_aus_tokens(self):
        css = render_back_link_css()
        assert "var(--web-touch-target" in css
        assert "var(--web-text-ui" in css
        assert ":hover" in css
        assert "var(--color-light-accent" in css
        assert ":focus-visible" in css
        assert "var(--web-stroke-focus" in css
        assert "var(--web-color-focus-ring" in css
        assert "var(--space-4" in css
        assert "var(--color-light-text-muted" in css
