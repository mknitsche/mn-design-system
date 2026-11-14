"""Kompakte Unterleiste im echten Browser (0.24.0): eine Zeile am Handy, Schalter nur dort."""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns.contracts import (
    SubNavGruppe,
    SubNavInput,
    SubNavTab,
    WebTier,
)
from mn_design_system.components.web import (
    render_font_face,
    render_foundation_css,
    web_font_dir,
)
from mn_design_system.components.web.sub_nav import (
    render_sub_nav_css,
    render_sub_nav_html,
)


def _t(label: str, href: str, active: bool = False) -> SubNavTab:
    return SubNavTab(label=label, href=href, active=active)


def _eingabe(aktiv: str) -> SubNavInput:
    du = ["Profil", "Gesundheit", "Befunde", "Sport"]
    system = ["Sessions", "Nachtlauf", "Berichte", "Briefing-Lauf"]
    return SubNavInput(
        tier=WebTier.OBSERVATORIUM,
        form="kompakt",
        tabs=[_t("Übersicht", "/o/", aktiv == "Übersicht")],
        gruppen=[
            SubNavGruppe(label="Du", tabs=[_t(n, f"/du/{n}/", n == aktiv) for n in du]),
            SubNavGruppe(
                label="System", tabs=[_t(n, f"/sys/{n}/", n == aktiv) for n in system]
            ),
        ],
    )


MESSEN = """() => {
  const sichtbar = (e) => getComputedStyle(e).display !== 'none';
  const r = (e) => e.getBoundingClientRect();
  const nav = document.querySelector('.mn-sub-nav');
  const tabs = [...nav.querySelectorAll('.mn-sub-nav__tab')].filter(sichtbar);
  const felder = [...nav.querySelectorAll('.mn-sub-nav__feld')];
  const schalter = nav.querySelector('.mn-sub-nav__schalter');
  const inner = nav.querySelector('.mn-sub-nav__inner');
  return {
    tabs: tabs.map((t) => t.textContent),
    zeilen: new Set(tabs.map((t) => Math.round(r(t).top))).size,
    minHoehe: Math.min(...tabs.map((t) => r(t).height)),
    seitlichScrollbar: inner.scrollWidth > inner.clientWidth + 1,
    seiteBreiter: document.documentElement.scrollWidth > window.innerWidth,
    schalterSichtbar: sichtbar(schalter),
    felder: felder.length,
    feldHoehe: felder.length ? Math.min(...felder.map((f) => r(f).height)) : 0,
    gruppenMarken: [...nav.querySelectorAll('.mn-sub-nav__gruppe')].filter(sichtbar).length,
    navHoehe: r(nav).height,
  };
}"""


def _messe(seite_laden, aktiv: str, breite: int):
    ctx, page = seite_laden(
        render_sub_nav_html(_eingabe(aktiv)),
        # die echte Schrift (Geist), nicht der Systemrueckfall: sie bestimmt die Breite
        render_font_face(web_font_dir().as_uri() + "/")
        + render_foundation_css()
        + render_sub_nav_css(kompakt=True),
        breite=breite,
    )
    try:
        return page.evaluate(MESSEN)
    finally:
        ctx.close()


@pytest.mark.parametrize("aktiv", ["Übersicht", "Gesundheit", "Briefing-Lauf"])
def test_handy_eine_zeile_ohne_scrollen_und_44px(seite_laden, aktiv):
    m = _messe(seite_laden, aktiv, 390)
    assert m["zeilen"] == 1, m
    assert not m["seitlichScrollbar"] and not m["seiteBreiter"], m
    assert m["minHoehe"] >= 44, m
    assert m["schalterSichtbar"] and m["felder"] == 2 and m["feldHoehe"] >= 44, m
    assert m["gruppenMarken"] == 0, m
    # Uebersicht plus genau die Reiter der aktiven Gruppe
    assert len(m["tabs"]) == 5, m
    assert m["tabs"][0] == "Übersicht", m


def test_handy_zeigt_nur_die_aktive_gruppe(seite_laden):
    m = _messe(seite_laden, "Berichte", 390)
    assert "Sessions" in m["tabs"] and "Profil" not in m["tabs"], m


def test_rechner_alles_in_einer_leiste_ohne_schalter(seite_laden):
    m = _messe(seite_laden, "Sport", 1400)
    assert not m["schalterSichtbar"], m
    assert m["gruppenMarken"] == 2, m
    assert len(m["tabs"]) == 9, m
    assert m["zeilen"] == 1, m
    assert m["minHoehe"] >= 44, m


def test_unterleiste_am_handy_hoehe(seite_laden):
    m = _messe(seite_laden, "Übersicht", 390)
    # Schalter + Reiterzeile; der Kopf kommt in T5 dazu (Budget Observatorium <= 140 px)
    assert m["navHoehe"] <= 96, m


@pytest.mark.parametrize("breite", [320, 360])
@pytest.mark.parametrize("aktiv", ["Übersicht", "Briefing-Lauf"])
def test_schmal_kein_seitlicher_seitenscroll(seite_laden, aktiv, breite):
    # Netz: passt die Zeile nicht, scrollt nur die Leiste, nie das Dokument
    m = _messe(seite_laden, aktiv, breite)
    assert not m["seiteBreiter"], (breite, m)
