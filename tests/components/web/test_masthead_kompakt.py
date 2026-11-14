"""Masthead 0.24.0: kompakte Form mit Blicken, Raum-Schalter und Rueckfall-Link (Plan T5)."""

from __future__ import annotations

import re

import pytest
from golden.faelle import pruefe_praefix
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    WebTier,
)
from mn_design_system.components.web.masthead import (
    render_masthead_css,
    render_masthead_html,
)


def _eingabe(**kw) -> MastheadInput:
    base = {
        "emblem": MastheadEmblem(src="/assets/logo.svg", alt="MKN", href="/start/"),
        "wordmark": "MKN 2nd Brain",
        "edition_date": "Samstag, 14. November",
        "tier_items": [
            MastheadTierItem(
                label="Start", href="/start/", tier=WebTier.START, active=True
            ),
            MastheadTierItem(label="Heute", href="/heute/", tier=WebTier.START),
            MastheadTierItem(label="Atelier", href="/atelier/", tier=WebTier.ATELIER),
            MastheadTierItem(
                label="Kabinett", href="/kabinett/", tier=WebTier.KABINETT
            ),
        ],
        "user_chip_id": "profil",
    }
    base.update(kw)
    return MastheadInput(**base)


def _kompakt(**kw) -> MastheadInput:
    kw.setdefault("raum_schalter", "Räume")
    return _eingabe(form="kompakt", blicke=2, **kw)


def test_alte_eingaben_rendern_wie_0_23_0():
    pruefe_praefix("masthead")


def test_klassisch_ist_der_default():
    i = _eingabe()
    assert (i.form, i.blicke, i.raum_schalter) == ("klassisch", 0, None)
    assert "kompakt" not in render_masthead_html(i)


def test_neue_felder_nur_in_der_kompakten_form():
    with pytest.raises(ValidationError):
        _eingabe(blicke=2)
    with pytest.raises(ValidationError):
        _eingabe(raum_schalter="Räume")


def test_blicke_nicht_mehr_als_eintraege():
    with pytest.raises(ValidationError):
        _eingabe(form="kompakt", blicke=5)
    with pytest.raises(ValidationError):
        _eingabe(form="kompakt", blicke=-1)


def test_kompakt_traegt_knopf_und_rueckfall_link():
    html = render_masthead_html(_kompakt(raum_schalter="Atelier"))
    knopf = re.findall(
        r'<button[^>]*popovertarget="raumplan"[^>]*>(.*?)</button>', html
    )
    link = re.findall(r'<a [^>]*href="#raumplan"[^>]*>(.*?)</a>', html)
    assert len(knopf) == 1 and len(link) == 1
    for inhalt in (knopf[0], link[0]):
        text = re.sub(r"<[^>]+>", "", inhalt)
        assert text.startswith("Atelier") and text.endswith("▾")
        # nur der Name kuerzt, der Pfeil ist ein eigenes Element
        assert '<span class="mn-masthead__raum-name">Atelier</span>' in inhalt
        assert (
            '<span class="mn-masthead__raum-pfeil" aria-hidden="true">▾</span>'
            in inhalt
        )
    assert 'type="button"' in html
    assert 'aria-controls="raumplan"' in html or "popovertarget" in html


def test_raum_pillen_tragen_ihre_klasse_blicke_nicht():
    html = render_masthead_html(_kompakt())
    pillen = re.findall(
        r'<a class="([^"]*mn-masthead__pill[^"]*)"[^>]*>([^<]*)</a>', html
    )
    raum = {t for k, t in pillen if "mn-masthead__pill--raum" in k}
    assert raum == {"Atelier", "Kabinett"}
    assert len(pillen) == 4


def test_ohne_raum_schalter_kein_knopf():
    html = render_masthead_html(_eingabe(form="kompakt", blicke=2))
    assert "popovertarget" not in html and "#raumplan" not in html


def test_aktiver_raum_bleibt_genau_einmal_aktiv():
    html = render_masthead_html(_kompakt())
    assert html.count("is-active") == 1
    assert html.count('aria-current="page"') == 1


def test_maskiert():
    html = render_masthead_html(_kompakt(raum_schalter="<b>R</b>"))
    assert "<b>" not in html and "&lt;b&gt;R&lt;/b&gt;" in html


def test_css_ohne_flag_ist_das_alte_css():
    assert render_masthead_css() == render_masthead_css(kompakt=False)
    assert render_masthead_css(kompakt=True).startswith(render_masthead_css())


def test_kompakt_css_kein_rohwert():
    css = render_masthead_css(kompakt=True)
    neu = css[len(render_masthead_css()) :]
    assert "mn-masthead--kompakt" in neu
    ohne_var = re.sub(r"@media \([^)]*\)", "", neu)
    ohne_var = re.sub(r"@supports [^{]*\{", "{", ohne_var)
    ohne_var = re.sub(
        r"rgba\([^()]*\)", "", ohne_var
    )  # Rueckfall in var(), verschachtelt
    while "var(" in ohne_var:
        ohne_var = re.sub(r"var\([^()]*\)", "", ohne_var)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var)
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne_var)
    assert "var(--web-touch-target" in neu


def test_kompakt_css_knopf_nur_unter_supports_sonst_link():
    neu = render_masthead_css(kompakt=True)
    assert "@supports selector(:popover-open)" in neu
    assert "@supports not selector(:popover-open)" not in neu  # Link ist der Standard
