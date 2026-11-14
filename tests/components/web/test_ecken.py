"""Eckenregel (0.24.0, Plan T24): Rollen-Variablen ueber den vorhandenen Radius-Tokens."""

from __future__ import annotations

import re

import pytest

from mn_design_system.components.web import (
    render_content_card_css,
    render_ecken_css,
    render_foundation_css,
    render_kachel_css,
    render_masthead_css,
    render_profilmenue_css,
    render_raumplan_css,
    render_sub_nav_css,
    render_tier_chip_css,
)

# Klasse -> Rolle (Spec 4.6): Flaeche, Bedienelement/Etikett (rund), Leiste (gerade)
ROLLEN = {
    "flaeche": [
        ".mn-kachel",
        ".mn-content-card",
        ".mn-kpi-card",
        ".mn-profilmenue",
        ".mn-aufklapper",
        ".mn-empty-state",
    ],
    "bedien": [
        ".mn-masthead__pill",
        ".mn-masthead__chip",
        ".mn-masthead__profil",
        ".mn-masthead__profil-link",
        ".mn-masthead__raum",
        ".mn-masthead__raum-link",
        ".mn-profilmenue__wahl",
        ".mn-raumplan__schliessen",
        ".mn-tier-chip",
        ".mn-status",
        ".mn-stand__tlp",
        ".mn-sub-nav__feld",
        ".mn-zeitraum-leiste__option",
        ".mn-chat-composer__btn",
    ],
    "leiste": [".mn-masthead", ".mn-masthead__identity", ".mn-sub-nav", ".mn-footer"],
}


def test_ecken_css_nur_tokens():
    css = render_ecken_css()
    assert render_ecken_css() == css  # parameterlos, deterministisch
    # die vier Rollen-Variablen stehen auf :root und haengen an den vorhandenen Radius-Tokens
    assert "--mn-r-flaeche: var(--radius-card" in css
    assert "--mn-r-bedien: var(--radius-round" in css
    assert "--mn-r-leiste: var(--radius-none" in css
    assert re.search(
        r"--mn-r-innen: max\(0px, calc\(var\(--mn-r-flaeche\) - var\(--space-4", css
    )
    # jeder Radius in den Regeln ist eine Rollen-Variable, nie ein Mass
    werte = re.findall(r"border-radius:\s*([^;]+);", css)
    assert werte
    for wert in werte:
        assert re.fullmatch(r"(var\(--mn-r-[a-z]+\)\s*)+(0\s*)*", wert.strip()), wert
    # kein Hex, kein rohes Mass (ausser der Null-Untergrenze `0px` der Innenregel)
    ohne = css.replace("max(0px,", "max(0,")
    ohne = re.sub(r"@media \([^)]*\)", "", ohne)
    ohne = re.sub(r"@supports [^{]*\{", "{", ohne)
    while "var(" in ohne:
        ohne = re.sub(r"var\([^()]*\)", "", ohne)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne), ohne
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne), ohne


def test_ecken_regeln_nennen_alle_klassen_ihrer_rolle():
    css = render_ecken_css()
    for rolle, klassen in ROLLEN.items():
        for klasse in klassen:
            muster = re.compile(
                r"(^|[\s,}])"
                + re.escape(klasse)
                + r"(?![\w-])[^{]*\{[^}]*--mn-r-"
                + ("flaeche" if rolle == "flaeche" else rolle),
                re.DOTALL,
            )
            assert muster.search(css), f"{klasse} ({rolle}) fehlt in der Eckenregel"


@pytest.fixture(scope="module")
def _seite_css():
    return (
        render_foundation_css()
        + render_masthead_css(kompakt=True)
        + render_sub_nav_css(kompakt=True)
        + render_kachel_css()
        + render_content_card_css()
        + render_tier_chip_css()
        + render_profilmenue_css()
        + render_raumplan_css()
        + render_ecken_css()
    )


def _radius(page, selektor):
    return page.evaluate(
        "(s) => getComputedStyle(document.querySelector(s)).borderTopLeftRadius",
        selektor,
    )


def test_ecken_rollen_im_browser(seite_laden, _seite_css):
    koerper = "".join(
        f'<div class="{k[1:]}" id="x{i}{r}">x</div>'
        for r, ks in ROLLEN.items()
        for i, k in enumerate(ks[:3])
    )
    ctx, page = seite_laden(koerper, _seite_css, breite=1200)
    try:
        for i in range(3):
            assert _radius(page, f"#x{i}flaeche") == "4px"  # radius-card
            assert _radius(page, f"#x{i}leiste") == "0px"  # radius-none
            r = _radius(page, f"#x{i}bedien")
            assert float(r.removesuffix("px")) >= 1000, r  # radius-round
    finally:
        ctx.close()


@pytest.mark.parametrize(
    ("aussen", "erwartet"),
    [
        ("20px", "4px"),
        ("16px", "0px"),
        ("10px", "0px"),
        ("4px", "0px"),
        ("40px", "24px"),
    ],
)
def test_ecken_innen_gleich_aussen_minus_abstand(
    seite_laden, _seite_css, aussen, erwartet
):
    # Innenabstand der Flaeche ist `space.4` (16px); nie weniger als 0
    ctx, page = seite_laden(
        '<div class="mn-kachel"><div class="mn-innen" id="i">x</div></div>',
        _seite_css,
        breite=1200,
    )
    try:
        page.evaluate(
            "(r) => document.documentElement.style.setProperty('--mn-r-flaeche', r)",
            aussen,
        )
        assert _radius(page, "#i") == erwartet
    finally:
        ctx.close()
