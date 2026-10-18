"""Tests fuer die Pfadzeile (0.20.0, Magazin-Welle 0)."""

from __future__ import annotations

import re

import pytest

from mn_design_system.components._patterns.contracts import PfadZeileInput
from mn_design_system.components.web import (
    render_pfad_zeile_css,
    render_pfad_zeile_html,
)


def test_leere_vorfahren_ergeben_nichts():
    assert render_pfad_zeile_html(PfadZeileInput(vorfahren=())) == ""
    assert render_pfad_zeile_html(PfadZeileInput()) == ""


def test_vorfahren_als_links_mit_trenner():
    html = render_pfad_zeile_html(
        PfadZeileInput(
            vorfahren=(
                ("archiv", "/magazin/dateien/archiv/"),
                ("briefing", "/magazin/dateien/archiv/briefing/"),
            )
        )
    )
    assert html.startswith('<nav class="mn-pfad-zeile"')
    assert 'aria-label="Pfad"' in html
    sichtbar = re.sub(r"<[^>]+>", "|", html)
    assert re.search(r"archiv\|+ \|*›\|+ \|*briefing\|+ \|*›", sichtbar), sichtbar
    assert html.count("<a ") == 2
    # der Trenner ist Zierde
    assert 'aria-hidden="true"' in html


def test_maskiert():
    html = render_pfad_zeile_html(PfadZeileInput(vorfahren=(("<b>&", '/x"y'),)))
    assert "<b>" not in html
    assert "&lt;b&gt;&amp;" in html
    assert '"y' not in html.replace("&quot;y", "")


@pytest.mark.parametrize(
    "href", ["javascript:x", "//evil.example/", "https://x.example/", "/a\\b"]
)
def test_fremde_ziele_werden_abgewiesen(href):
    with pytest.raises(ValueError):
        PfadZeileInput(vorfahren=(("x", href),))


def test_css_nur_var():
    css = render_pfad_zeile_css()
    assert ".mn-pfad-zeile" in css
    ohne_var = css
    while "var(" in ohne_var:
        ohne_var = re.sub(r"var\([^()]*\)", "", ohne_var)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var)
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne_var)
    for token in ("--web-text-ui", "--color-light-text-muted", "--color-light-accent"):
        assert f"var({token}" in css


def test_inline_css():
    p = PfadZeileInput(vorfahren=(("a", "/a/"),))
    assert render_pfad_zeile_html(p, inline_css=True).startswith("<style>")
    assert "<style" not in render_pfad_zeile_html(p)
