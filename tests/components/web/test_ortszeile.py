"""Tests fuer die Ortszeile (0.24.0, Welle 1): die ganze Kette, das letzte Glied ist die Eltern-Seite."""

from __future__ import annotations

import re

import pytest
from golden.faelle import pruefe_praefix
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import OrtszeileInput
from mn_design_system.components.web import (
    render_ortszeile_css,
    render_ortszeile_html,
)

KETTE = (
    ("/observatorium/", "Observatorium"),
    ("/observatorium/gesundheit/", "Gesundheit"),
    ("/observatorium/gesundheit/schlaf/", "Schlaf"),
)


def test_alte_eingaben_rendern_wie_0_23_0():
    # Pfadzeile und Zurueck-Zeile bleiben, wie sie waren (die Ortszeile ersetzt sie nicht)
    pruefe_praefix("pfad_zeile")
    pruefe_praefix("back_link")


def test_struktur_nav_ol_li_a():
    html = render_ortszeile_html(OrtszeileInput(glieder=KETTE))
    assert html.startswith('<nav class="mn-ortszeile" aria-label="Ort"><ol>')
    assert html.endswith("</ol></nav>")
    assert html.count("<li>") == 3
    assert html.count("<a ") == 3


def test_aria_label_ist_gesetzt():
    assert 'aria-label="Ort"' in render_ortszeile_html(OrtszeileInput(glieder=KETTE))


def test_genau_ein_eltern_und_es_ist_das_letzte_glied():
    html = render_ortszeile_html(OrtszeileInput(glieder=KETTE))
    assert html.count("mn-ortszeile__eltern") == 1
    letztes = re.findall(r"<li>(.*?)</li>", html)[-1]
    assert 'class="mn-ortszeile__eltern"' in letztes
    assert ">← Schlaf</a>" in letztes
    # die Vorfahren tragen keinen Pfeil
    assert html.count("←") == 1


def test_ein_glied_ist_zugleich_das_eltern_glied():
    html = render_ortszeile_html(OrtszeileInput(glieder=(("/start/", "Start"),)))
    assert html.count("<li>") == 1
    assert '<a class="mn-ortszeile__eltern" href="/start/">← Start</a>' in html


def test_maskiert():
    html = render_ortszeile_html(
        OrtszeileInput(glieder=(("/a/", "<b>&"), ("/b/", "<i>x</i>")))
    )
    assert "<b>" not in html
    assert "<i>" not in html
    assert "&lt;b&gt;&amp;" in html
    assert "&lt;i&gt;x&lt;/i&gt;" in html


def test_leere_kette_wird_abgewiesen():
    with pytest.raises(ValidationError):
        OrtszeileInput(glieder=())


@pytest.mark.parametrize(
    "href", ["javascript:x", "//evil.example/", "https://x.example/", "/a\\b"]
)
def test_fremde_ziele_werden_abgewiesen(href):
    with pytest.raises(ValueError):
        OrtszeileInput(glieder=(("/ok/", "ok"), (href, "x")))


def test_leeres_label_wird_abgewiesen():
    with pytest.raises(ValueError):
        OrtszeileInput(glieder=(("/a/", ""),))


def test_css_einzeilig_letztes_glied_schrumpft_nie():
    css = render_ortszeile_css()
    assert "flex-wrap: nowrap" in css
    assert "text-overflow: ellipsis" in css
    letztes = re.search(r"\.mn-ortszeile li:last-child\s*\{([^}]*)\}", css)
    assert letztes, css
    assert "flex: none" in letztes.group(1)
    vorher = re.search(r"\.mn-ortszeile li:not\(:last-child\)\s*\{([^}]*)\}", css)
    assert vorher, css
    assert "min-width: 0" in vorher.group(1)


def test_css_kein_rohwert():
    css = render_ortszeile_css()
    ohne_var = css
    while "var(" in ohne_var:
        ohne_var = re.sub(r"var\([^()]*\)", "", ohne_var)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var)
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne_var)
    for token in ("--web-text-ui", "--color-light-text-muted", "--web-touch-target"):
        assert f"var({token}" in css


def test_inline_css():
    p = OrtszeileInput(glieder=(("/a/", "a"),))
    assert render_ortszeile_html(p, inline_css=True).startswith("<style>")
    assert "<style" not in render_ortszeile_html(p)
