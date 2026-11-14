"""Sub-Nav 0.24.0: kompakte Form mit Gruppen und Gruppen-Schalter (Welle 1, Plan T4)."""

from __future__ import annotations

import re

import pytest
from golden.faelle import pruefe_praefix
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    SubNavGruppe,
    SubNavInput,
    SubNavTab,
    WebTier,
)
from mn_design_system.components.web.sub_nav import (
    render_sub_nav_css,
    render_sub_nav_html,
)
from mn_design_system.tokens import get


def _tabs(*namen: str, aktiv: str | None = None, basis: str = "/o/") -> list[SubNavTab]:
    return [
        SubNavTab(label=n, href=f"{basis}{n.lower()}/", active=n == aktiv)
        for n in namen
    ]


def _kompakt(aktiv: str = "Übersicht", **kw) -> SubNavInput:
    du = _tabs("Profil", "Gesundheit", "Befunde", "Sport", aktiv=aktiv, basis="/du/")
    system = _tabs("Sessions", "Nachtlauf", "Berichte", aktiv=aktiv, basis="/sys/")
    base = {
        "tier": WebTier.OBSERVATORIUM,
        "form": "kompakt",
        "tabs": _tabs("Übersicht", aktiv=aktiv, basis="/ue/"),
        "gruppen": [
            SubNavGruppe(label="Du", tabs=du),
            SubNavGruppe(label="System", tabs=system),
        ],
    }
    base.update(kw)
    return SubNavInput(**base)


def _schalter(html: str) -> str:
    m = re.search(r'<div class="mn-sub-nav__schalter".*?</div>', html, re.DOTALL)
    assert m, html
    return m.group(0)


def test_alte_eingaben_rendern_wie_0_23_0():
    pruefe_praefix("sub_nav")


def test_klassisch_ist_der_default():
    i = SubNavInput(tier=WebTier.ATELIER, tabs=_tabs("A"))
    assert i.form == "klassisch"
    assert i.gruppen is None


def test_klassisch_zehn_reiter_bleiben_erlaubt():
    namen = [f"T{n}" for n in range(10)]
    i = SubNavInput(tier=WebTier.ATELIER, tabs=_tabs(*namen, aktiv="T0"))
    html = render_sub_nav_html(i)
    assert html.count('class="mn-sub-nav__tab') == 10
    assert "mn-sub-nav__schalter" not in html


def test_klassisch_nimmt_keine_gruppen():
    with pytest.raises(ValidationError):
        SubNavInput(
            tier=WebTier.ATELIER,
            tabs=_tabs("A"),
            gruppen=[SubNavGruppe(label="G", tabs=_tabs("B"))],
        )


def test_kompakt_mehr_als_fuenf_je_gruppe_wird_abgewiesen():
    # 1 Uebersicht + 5 in der Gruppe = 6
    zu_viele = SubNavGruppe(label="G", tabs=_tabs("A", "B", "C", "D", "E"))
    with pytest.raises(ValidationError, match="fuenf"):
        SubNavInput(
            tier=WebTier.ATELIER,
            form="kompakt",
            tabs=_tabs("Übersicht", aktiv="Übersicht"),
            gruppen=[zu_viele],
        )


def test_kompakt_genau_fuenf_je_gruppe_sind_erlaubt():
    ok = SubNavGruppe(label="G", tabs=_tabs("A", "B", "C", "D"))
    SubNavInput(
        tier=WebTier.ATELIER,
        form="kompakt",
        tabs=_tabs("Übersicht", aktiv="Übersicht"),
        gruppen=[ok],
    )


def test_kompakt_ohne_gruppen_hoechstens_fuenf():
    with pytest.raises(ValidationError, match="fuenf"):
        SubNavInput(
            tier=WebTier.ATELIER,
            form="kompakt",
            tabs=_tabs("A", "B", "C", "D", "E", "F", aktiv="A"),
        )


@pytest.mark.parametrize("aktiv", [None, "zwei"])
def test_kompakt_genau_ein_reiter_aktiv(aktiv):
    tabs = _tabs("Übersicht", "B", aktiv=aktiv or "Übersicht")
    if aktiv == "zwei":
        tabs = [t.model_copy(update={"active": True}) for t in tabs]
    else:
        tabs = [t.model_copy(update={"active": False}) for t in tabs]
    with pytest.raises(ValidationError, match="aktiv"):
        SubNavInput(tier=WebTier.ATELIER, form="kompakt", tabs=tabs)


def test_kompakt_aktiv_in_einer_gruppe_zaehlt():
    i = _kompakt(aktiv="Sport")
    html = render_sub_nav_html(i)
    assert html.count("is-active") == 2  # Reiter Sport + Schalterfeld „Du“


def test_schalter_verlinkt_nur_erste_reiter_der_eigenen_gruppen():
    schalter = _schalter(render_sub_nav_html(_kompakt()))
    hrefs = re.findall(r'href="([^"]+)"', schalter)
    assert hrefs == ["/du/profil/", "/sys/sessions/"]
    assert 'role="group"' in schalter
    assert schalter.count("<a ") == 2
    assert ">Du</a>" in schalter and ">System</a>" in schalter


def test_genau_ein_schalterfeld_aktiv():
    for aktiv, erwartet in [("Sport", "Du"), ("Nachtlauf", "System")]:
        schalter = _schalter(render_sub_nav_html(_kompakt(aktiv=aktiv)))
        aktive = re.findall(
            r'<a class="mn-sub-nav__feld is-active"[^>]*>(.*?)</a>', schalter
        )
        assert aktive == [erwartet], (aktiv, schalter)
        assert schalter.count("is-active") == 1


def test_uebersicht_aktiv_waehlt_erste_gruppe():
    html = render_sub_nav_html(_kompakt(aktiv="Übersicht"))
    schalter = _schalter(html)
    assert re.findall(r'is-active"[^>]*>(.*?)</a>', schalter) == ["Du"]
    # darunter: nur Uebersicht und die Reiter der aktiven Gruppe — die andere ist ausgeblendet
    assert html.count('data-gruppe-aktiv="true"') == 4 + 1  # vier Reiter + Gruppenmarke
    assert html.count('data-gruppe-aktiv="false"') == 3 + 1


def test_aktive_gruppe_markiert_nur_ihre_reiter():
    html = render_sub_nav_html(_kompakt(aktiv="Berichte"))
    # 3 Reiter + Marke der Gruppe System sind aktiv, Du ist aus
    teile = re.findall(r'data-gruppe-aktiv="(true|false)"[^>]*>([^<]*)<', html)
    aktiv = [t for z, t in teile if z == "true"]
    assert "Sessions" in aktiv and "Berichte" in aktiv and "System" in aktiv
    assert "Profil" not in aktiv


def test_genau_ein_aria_current_page():
    html = render_sub_nav_html(_kompakt(aktiv="Befunde"))
    assert html.count('aria-current="page"') == 1


def test_maskiert():
    i = SubNavInput(
        tier=WebTier.ATELIER,
        form="kompakt",
        tabs=_tabs("Übersicht", aktiv="Übersicht"),
        gruppen=[
            SubNavGruppe(
                label="<b>G</b>",
                tabs=[SubNavTab(label="<i>x</i>", href='/x"><script>')],
            )
        ],
    )
    html = render_sub_nav_html(i)
    assert "<b>" not in html and "<i>" not in html and "<script>" not in html
    assert "&lt;b&gt;G&lt;/b&gt;" in html


def test_kompakt_css_ohne_flag_ist_das_alte_css():
    assert render_sub_nav_css() == render_sub_nav_css(kompakt=False)
    assert render_sub_nav_css(kompakt=True).startswith(render_sub_nav_css())


def test_kompakt_css_kein_rohwert():
    css = render_sub_nav_css(kompakt=True)
    neu = css[len(render_sub_nav_css()) :]
    assert "mn-sub-nav__schalter" in neu
    # die Media-Query-Schwellen kommen aus den Tokens (media_max_width_below / get)
    ohne_var = re.sub(r"@media \([^)]*\)", "", neu)
    while "var(" in ohne_var:
        ohne_var = re.sub(r"var\([^()]*\)", "", ohne_var)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var)
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne_var)
    assert "var(--web-touch-target" in neu


def test_kompakt_css_schalter_nur_am_handy():
    neu = render_sub_nav_css(kompakt=True)[len(render_sub_nav_css()) :]
    # ausserhalb jeder Media-Query ist der Schalter aus
    vor_media = neu.split("@media", 1)[0]
    assert re.search(r"\.mn-sub-nav__schalter\s*\{\s*display:\s*none", vor_media)
    assert f"max-width: {get('web.layout.bp-mobile')}" in neu
