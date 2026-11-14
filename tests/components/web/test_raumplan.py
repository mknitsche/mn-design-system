"""Raumplan (0.24.0, Welle 1, Plan T5): Blatt unter @supports, sonst sichtbarer Abschnitt."""

from __future__ import annotations

import re

import pytest
from golden.faelle import pruefe_praefix
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    RaumplanInput,
    RaumplanRaum,
)
from mn_design_system.components.web import (
    render_raumplan_css,
    render_raumplan_html,
)


def _eingabe() -> RaumplanInput:
    return RaumplanInput(
        raeume=[
            RaumplanRaum(
                slug="bibliothek",
                label="Bibliothek",
                href="/bibliothek/",
                zweck="Lesen und Nachschlagen",
                reiter=[("Übersicht", "/bibliothek/"), ("Berichte", "/bibliothek/b/")],
            ),
            RaumplanRaum(
                slug="observatorium",
                label="Observatorium",
                href="/observatorium/",
                zweck="Zustand und Verlauf",
                reiter=[("Übersicht", "/observatorium/")],
                gruppen=[
                    ("Du", [("Profil", "/du/profil/"), ("Sport", "/du/sport/")]),
                    ("System", [("Sessions", "/sys/sessions/")]),
                ],
            ),
        ]
    )


def test_alte_eingaben_rendern_wie_0_23_0():
    # der Raumplan ist neu; die bestehende Kopf- und Unterleisten-Ausgabe bleibt gleich
    pruefe_praefix("masthead")
    pruefe_praefix("sub_nav")


def test_struktur():
    html = render_raumplan_html(_eingabe())
    assert html.startswith(
        '<section id="raumplan" class="mn-raumplan" popover '
        'aria-labelledby="raumplan-titel">'
    )
    assert '<h2 id="raumplan-titel"' in html and ">Alle Räume</h2>" in html
    assert html.count('data-bereich="') == 2
    assert 'data-bereich="bibliothek"' in html
    assert 'data-bereich="observatorium"' in html


def test_titel_ueberschreibbar():
    html = render_raumplan_html(RaumplanInput(raeume=_eingabe().raeume, titel="Orte"))
    assert ">Orte</h2>" in html


def test_raumplan_enthaelt_genau_die_uebergebenen_links():
    html = render_raumplan_html(_eingabe())
    erwartet = {
        "/bibliothek/",
        "/bibliothek/b/",
        "/observatorium/",
        "/du/profil/",
        "/du/sport/",
        "/sys/sessions/",
    }
    assert set(re.findall(r'<a [^>]*href="([^"]+)"', html)) == erwartet
    # keine Verweise ausser den uebergebenen (kein Duplikat-Link, keine Sprungmarke)
    assert html.count("<a ") == len(re.findall(r'<a [^>]*href="([^"]+)"', html))
    assert "#" not in "".join(re.findall(r'href="([^"]+)"', html))


def test_zweck_und_gruppen_stehen_im_raum():
    html = render_raumplan_html(_eingabe())
    obs = html.split('data-bereich="observatorium"')[1]  # der letzte Raum bis zum Ende
    assert "Zustand und Verlauf" in obs
    assert ">Du<" in obs and ">System<" in obs
    assert "Zustand und Verlauf" not in html.split('data-bereich="observatorium"')[0]


def test_maskiert():
    html = render_raumplan_html(
        RaumplanInput(
            raeume=[
                RaumplanRaum(
                    slug='x"><script>',
                    label="<b>R</b>",
                    href="/r/",
                    zweck="<i>z</i>",
                    reiter=[("<u>t</u>", "/r/t/")],
                )
            ],
            titel="<s>T</s>",
        )
    )
    for roh in ("<b>", "<i>", "<u>", "<s>", "<script>"):
        assert roh not in html
    assert "&lt;b&gt;R&lt;/b&gt;" in html


def test_leere_raumliste_wird_abgewiesen():
    with pytest.raises(ValidationError):
        RaumplanInput(raeume=[])


@pytest.mark.parametrize(
    "href", ["javascript:x", "//evil.example/", "https://x.example/"]
)
def test_fremde_ziele_werden_abgewiesen(href):
    with pytest.raises(ValueError):
        RaumplanRaum(slug="a", label="A", href=href, zweck="z", reiter=[])
    with pytest.raises(ValueError):
        RaumplanRaum(slug="a", label="A", href="/a/", zweck="z", reiter=[("t", href)])
    with pytest.raises(ValueError):
        RaumplanRaum(
            slug="a",
            label="A",
            href="/a/",
            zweck="z",
            reiter=[],
            gruppen=[("G", [("t", href)])],
        )


def test_raumplan_css_blatt_nur_unter_supports():
    css = render_raumplan_css()
    # Blatt (feste Lage unten) steht ausschliesslich im @supports-Block
    vor = css.split("@supports", 1)[0]
    assert "position: fixed" not in vor
    assert "@supports selector(:popover-open)" in css
    unter = css.split("@supports selector(:popover-open)", 1)[1]
    assert "position: fixed" in unter
    # der Rueckfall bleibt sichtbar, auch wo die UA-Regel [popover] verbirgt
    assert re.search(
        r"@supports not selector\(:popover-open\)\s*\{\s*\.mn-raumplan\s*\{[^}]*display:\s*block",
        css,
    ), css


def test_raumplan_css_kein_rohwert():
    css = render_raumplan_css()
    ohne_var = css
    while "var(" in ohne_var:
        ohne_var = re.sub(r"var\([^()]*\)", "", ohne_var)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var)
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em|vh|dvh|vw)\b", ohne_var)


def test_inline_css():
    assert render_raumplan_html(_eingabe(), inline_css=True).startswith("<style>")
    assert "<style" not in render_raumplan_html(_eingabe())
