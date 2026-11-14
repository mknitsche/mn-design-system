"""Profil-Knopf, Profil-Menue, Schema-Skript und Kopf ohne Trenner (0.24.0, Plan T24)."""

from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    ProfilMenueInput,
    WebTier,
)
from mn_design_system.components.web import (
    render_masthead_css,
    render_masthead_html,
    render_profilmenue_css,
    render_profilmenue_html,
    render_schema_js,
)


def _kopf(**kw) -> MastheadInput:
    base = {
        "emblem": MastheadEmblem(src="/assets/logo.svg", alt="MKN", href="/start/"),
        "wordmark": "MKN 2nd Brain",
        "tier_items": [
            MastheadTierItem(
                label="Start", href="/start/", tier=WebTier.START, active=True
            ),
            MastheadTierItem(label="Heute", href="/heute/", tier=WebTier.START),
            MastheadTierItem(label="Atelier", href="/atelier/", tier=WebTier.ATELIER),
        ],
    }
    base.update(kw)
    return MastheadInput(**base)


def test_kompakt_ohne_trenner():
    i = _kopf(form="kompakt", blicke=2, raum_schalter="Räume")
    html = render_masthead_html(i)
    assert "trenner" not in html
    assert "trenner" not in render_masthead_css(kompakt=True)
    # blicke bestimmt weiter, welche Pillen am Handy sichtbar bleiben
    pillen = {
        t: k
        for k, t in re.findall(
            r'<a class="([^"]*mn-masthead__pill[^"]*)"[^>]*>([^<]*)</a>', html
        )
    }
    assert "mn-masthead__pill--raum" in pillen["Atelier"]
    assert "mn-masthead__pill--raum" not in pillen["Heute"]


def test_profilmenue_knopf_und_drei_zustaende():
    profil = ProfilMenueInput(profil_href="/start/profil/")
    kopf = render_masthead_html(_kopf(profil=profil))
    knoepfe = re.findall(r"<button[^>]*mn-masthead__profil[^>]*>", kopf)
    assert len(knoepfe) == 1
    k = knoepfe[0]
    for teil in (
        'type="button"',
        'popovertarget="profilmenue"',
        'aria-label="Profil und Darstellung"',
    ):
        assert teil in k, k
    # ohne Profil gibt es keinen Knopf (alte Eingaben unveraendert)
    assert "mn-masthead__profil" not in render_masthead_html(_kopf())

    menue = render_profilmenue_html(profil)
    assert re.match(r'<div id="profilmenue" class="mn-profilmenue" popover[ >]', menue)
    wahl = re.findall(r'<button[^>]*data-schema-wahl="([a-z]+)"[^>]*>', menue)
    assert wahl == ["auto", "hell", "dunkel"]
    assert menue.count("aria-pressed=") == 3
    assert menue.count('aria-pressed="true"') == 1  # genau ein Zustand gilt
    assert (
        '<a class="mn-profilmenue__link" href="/start/profil/">Profil ansehen</a>'
        in menue
    )
    assert menue.count("<a ") == 1


@pytest.mark.parametrize(
    "href",
    [
        "javascript:x",
        "//evil.example/",
        "https://x.example/",
        "relativ/",
        "/\\host",
        "/a\tb",
        "",
    ],
)
def test_profil_href_nur_intern(href):
    with pytest.raises(ValidationError):
        ProfilMenueInput(profil_href=href)
    assert ProfilMenueInput(profil_href="/ok/").titel == "Darstellung"


def test_titel_maskiert():
    html = render_profilmenue_html(
        ProfilMenueInput(profil_href="/p/", titel="<b>T</b>")
    )
    assert "<b>" not in html and "&lt;b&gt;T&lt;/b&gt;" in html


def test_css_kein_rohwert():
    css = render_profilmenue_css() + render_masthead_css(kompakt=True)
    neu = render_profilmenue_css()
    ohne = re.sub(r"@media \([^)]*\)", "", neu)
    ohne = re.sub(r"@supports [^{]*\{", "{", ohne)
    ohne = re.sub(r"rgba\([^()]*\)", "", ohne)
    while "var(" in ohne:
        ohne = re.sub(r"var\([^()]*\)", "", ohne)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne), ohne
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne), ohne
    assert css


def test_schema_js_parameterlos_ohne_inline_und_ohne_innerhtml():
    js = render_schema_js()
    assert "mn-schema" in js and "data-schema-wahl" in js
    assert "innerHTML" not in js and "eval(" not in js
    assert render_schema_js() == js
