"""Kompakter Kopf, Raum-Schalter und Raumplan im echten Browser (0.24.0, Plan T5)."""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns.contracts import (
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    RaumplanInput,
    RaumplanRaum,
    SubNavGruppe,
    SubNavInput,
    SubNavTab,
    WebTier,
)
from mn_design_system.components.web import (
    LOGO_KOPF_DATEI,
    logos_dir,
    render_font_face,
    render_foundation_css,
    render_masthead_css,
    render_masthead_html,
    render_raumplan_css,
    render_raumplan_html,
    render_sub_nav_css,
    render_sub_nav_html,
    web_font_dir,
)

_LOGO = (logos_dir() / LOGO_KOPF_DATEI).as_uri()


def _kopf() -> str:
    items = [
        ("Start", "/start/", WebTier.START),
        ("Heute", "/heute/", WebTier.START),
        ("Bibliothek", "/bibliothek/", WebTier.BIBLIOTHEK),
        ("Atelier", "/atelier/", WebTier.ATELIER),
        ("Kabinett", "/kabinett/", WebTier.KABINETT),
        ("Observatorium", "/observatorium/", WebTier.OBSERVATORIUM),
        ("Magazin", "/magazin/", WebTier.MAGAZIN),
    ]
    return render_masthead_html(
        MastheadInput(
            emblem=MastheadEmblem(src=_LOGO, alt="MKN", href="/start/"),
            wordmark="MKN 2nd Brain",
            edition_date="Samstag, 14. November",
            tier_items=[
                MastheadTierItem(label=l, href=h, tier=t, active=l == "Observatorium")
                for l, h, t in items
            ],
            user_chip_id="profil",
            user_chip_label="MN",
            form="kompakt",
            blicke=2,
            raum_schalter="Observatorium",
        )
    )


def _unterleiste(gruppen: bool) -> str:
    def t(label, href, active=False):
        return SubNavTab(label=label, href=href, active=active)

    if gruppen:
        eingabe = SubNavInput(
            tier=WebTier.OBSERVATORIUM,
            form="kompakt",
            tabs=[t("Übersicht", "/o/", True)],
            gruppen=[
                SubNavGruppe(
                    label="Du",
                    tabs=[
                        t(n, f"/du/{n}/")
                        for n in ("Profil", "Gesundheit", "Befunde", "Sport")
                    ],
                ),
                SubNavGruppe(
                    label="System",
                    tabs=[
                        t(n, f"/s/{n}/") for n in ("Sessions", "Nachtlauf", "Berichte")
                    ],
                ),
            ],
        )
    else:
        eingabe = SubNavInput(
            tier=WebTier.OBSERVATORIUM,
            form="kompakt",
            tabs=[t("Übersicht", "/o/", True)]
            + [t(n, f"/x/{n}/") for n in ("Zucker", "Schlaf", "Puls", "Gewicht")],
        )
    return render_sub_nav_html(eingabe)


def _raumplan() -> str:
    return render_raumplan_html(
        RaumplanInput(
            raeume=[
                RaumplanRaum(
                    slug=s,
                    label=l,
                    href=f"/{s}/",
                    zweck=f"Zweck {l}",
                    reiter=[("Übersicht", f"/{s}/"), ("Eins", f"/{s}/eins/")],
                )
                for s, l in (("bibliothek", "Bibliothek"), ("atelier", "Atelier"))
            ]
        )
    )


def _css(fallback_simulieren: bool = False) -> str:
    css = (
        render_font_face(web_font_dir().as_uri() + "/")
        + render_foundation_css()
        + render_masthead_css(kompakt=True)
        + render_sub_nav_css(kompakt=True)
        + render_raumplan_css()
    )
    if fallback_simulieren:
        # ein Browser, der :popover-open nicht kennt: dieselbe Seite, dieselben Regeln
        css = css.replace(
            "@supports selector(:popover-open)", "@supports selector(:kein-solcher)"
        ).replace(
            "@supports not selector(:popover-open)",
            "@supports not selector(:kein-solcher)",
        )
    return css


def _seite(gruppen: bool = False) -> str:
    return _kopf() + _unterleiste(gruppen) + "<main><p>Inhalt</p></main>" + _raumplan()


MESSEN = """() => {
  const sichtbar = (e) => !!e && getComputedStyle(e).display !== 'none';
  const r = (e) => e.getBoundingClientRect();
  const q = (s) => document.querySelector(s);
  const kopf = q('.mn-masthead');
  const nav = q('.mn-sub-nav');
  const pillen = [...document.querySelectorAll('.mn-masthead__pill')];
  return {
    kopfHoehe: r(kopf).height,
    kopfUnterleiste: r(nav).bottom - r(kopf).top,
    sichtbarePillen: pillen.filter(sichtbar).map((p) => p.textContent),
    pillenHoehe: Math.min(...pillen.filter(sichtbar).map((p) => r(p).height)),
    zeilen: new Set([q('.mn-masthead__emblem'), ...pillen.filter(sichtbar),
      q('.mn-masthead__raum'), q('.mn-masthead__raum-link'), q('#profil')]
      .filter(sichtbar).map((e) => Math.round(r(e).top + r(e).height / 2 / 20))).size,
    marke: sichtbar(q('.mn-masthead__brand')),
    knopf: sichtbar(q('.mn-masthead__raum')),
    link: sichtbar(q('.mn-masthead__raum-link')),
    knopfHoehe: sichtbar(q('.mn-masthead__raum')) ? r(q('.mn-masthead__raum')).height : 0,
    profil: sichtbar(q('#profil')),
    profilRechts: r(q('#profil')).right <= window.innerWidth,
    seiteBreiter: document.documentElement.scrollWidth > window.innerWidth,
    raumplanSichtbar: sichtbar(q('#raumplan')),
  };
}"""


def _messe(seite_laden, breite: int, gruppen: bool = False, fallback=False):
    ctx, page = seite_laden(_seite(gruppen), _css(fallback), breite=breite, hoehe=844)
    try:
        return page.evaluate(MESSEN)
    finally:
        ctx.close()


def test_handy_eine_zeile_mit_blicken_und_raum_schalter(seite_laden):
    m = _messe(seite_laden, 390)
    assert m["sichtbarePillen"] == ["Start", "Heute"], m
    assert not m["marke"], m
    assert m["knopf"] and not m["link"], m
    assert m["profil"] and m["profilRechts"] and not m["seiteBreiter"], m
    assert m["pillenHoehe"] >= 44 and m["knopfHoehe"] >= 44, m


def test_handy_kopf_plus_unterleiste_im_budget(seite_laden):
    # Plan: bei 390x844 belegen Kopf und Unterleiste <= 100 px, im Observatorium <= 140 px
    m = _messe(seite_laden, 390, gruppen=False)
    assert m["kopfUnterleiste"] <= 100, m
    m = _messe(seite_laden, 390, gruppen=True)
    assert m["kopfUnterleiste"] <= 140, m


def test_rechner_klassische_zeilen(seite_laden):
    m = _messe(seite_laden, 1400)
    assert len(m["sichtbarePillen"]) == 7, m
    assert m["marke"], m
    assert not m["knopf"] and not m["link"], m


def test_knopf_oeffnet_blatt_esc_schliesst_fokus_kehrt_zurueck(seite_laden):
    ctx, page = seite_laden(_seite(), _css(), breite=390, hoehe=844)
    try:
        assert not page.evaluate(
            "getComputedStyle(document.querySelector('#raumplan')).display !== 'none'"
        )
        page.click(".mn-masthead__raum")
        assert page.evaluate(
            "document.querySelector('#raumplan').matches(':popover-open')"
        )
        m = page.evaluate(
            """() => {
              const b = document.querySelector('#raumplan').getBoundingClientRect();
              return {unten: Math.round(b.bottom) === window.innerHeight,
                      links: document.querySelectorAll('#raumplan a').length,
                      breit: Math.round(b.width) === window.innerWidth};
            }"""
        )
        assert m == {"unten": True, "links": 6, "breit": True}, m
        page.keyboard.press("Escape")
        assert not page.evaluate(
            "document.querySelector('#raumplan').matches(':popover-open')"
        )
        assert page.evaluate(
            "document.activeElement.classList.contains('mn-masthead__raum')"
        )
    finally:
        ctx.close()


def test_schliessen_knopf_im_blatt(seite_laden):
    ctx, page = seite_laden(_seite(), _css(), breite=390, hoehe=844)
    try:
        page.click(".mn-masthead__raum")
        page.click(".mn-raumplan__schliessen")
        assert not page.evaluate(
            "document.querySelector('#raumplan').matches(':popover-open')"
        )
    finally:
        ctx.close()


def test_rueckfall_link_und_sichtbarer_abschnitt_ohne_popover_unterstuetzung(
    seite_laden,
):
    m = _messe(seite_laden, 390, fallback=True)
    assert m["link"] and not m["knopf"], m
    assert m["raumplanSichtbar"], m  # kein Raum wird unerreichbar
    ctx, page = seite_laden(_seite(), _css(True), breite=390, hoehe=844)
    try:
        assert page.evaluate(
            "getComputedStyle(document.querySelector('.mn-raumplan__schliessen')).display === 'none'"
        )
        page.click(".mn-masthead__raum-link")
        assert page.evaluate("location.hash") == "#raumplan"
    finally:
        ctx.close()


def test_schmal_kein_seitlicher_seitenscroll(seite_laden):
    for breite in (320, 360):
        m = _messe(seite_laden, breite, gruppen=True)
        assert not m["seiteBreiter"] and m["profilRechts"], (breite, m)


RAUM_MESSEN = """() => {
  const r = (e) => e.getBoundingClientRect();
  const k = document.querySelector('.mn-masthead__raum');
  const n = k.querySelector('.mn-masthead__raum-name');
  const p = k.querySelector('.mn-masthead__raum-pfeil');
  return {
    nameVoll: n.scrollWidth <= n.clientWidth,
    nameBreite: Math.round(n.clientWidth), nameNatuerlich: n.scrollWidth,
    pfeilSichtbar: r(p).width > 0 && r(p).right <= r(k).right + 1 && r(p).right <= window.innerWidth,
    seiteBreiter: document.documentElement.scrollWidth > window.innerWidth,
    profilRechts: r(document.querySelector('#profil')).right <= window.innerWidth,
  };
}"""


def _raum(seite_laden, breite):
    ctx, page = seite_laden(_seite(), _css(), breite=breite, hoehe=844)
    try:
        return page.evaluate(RAUM_MESSEN)
    finally:
        ctx.close()


def test_laengster_raumname_bei_390_voll_sichtbar(seite_laden):
    m = _raum(seite_laden, 390)  # „Observatorium“ ist der laengste Raumname
    assert m["nameVoll"] and m["pfeilSichtbar"] and not m["seiteBreiter"], m
    assert m["profilRechts"], m


def test_pfeil_bleibt_bei_schmalen_breiten_nur_der_name_kuerzt(seite_laden):
    for breite in (320, 360):
        m = _raum(seite_laden, breite)
        assert m["pfeilSichtbar"], (breite, m)
        assert not m["seiteBreiter"] and m["profilRechts"], (breite, m)


DESKTOP_MESSEN = """() => {
  const sichtbar = (e) => !!e && getComputedStyle(e).display !== 'none';
  const pillen = [...document.querySelectorAll('.mn-masthead__pill')];
  return {
    pillen: pillen.filter(sichtbar).length,
    marke: sichtbar(document.querySelector('.mn-masthead__brand')),
    knopf: sichtbar(document.querySelector('.mn-masthead__raum')),
    link: sichtbar(document.querySelector('.mn-masthead__raum-link')),
    blatt: sichtbar(document.querySelector('#raumplan')),
    zeilen: new Set(pillen.filter(sichtbar).map((p) => Math.round(p.getBoundingClientRect().top))).size,
  };
}"""


@pytest.mark.parametrize("breite", [800, 1280, 1440])
def test_desktop_und_tablet_zeigen_die_volle_raumleiste_ohne_schalter(
    seite_laden, breite
):
    # Spec 3.3: Rechner und iPad = sieben Pillen in einer Zeile; „Raum ▾“ ist die Handy-Form
    ctx, page = seite_laden(_seite(), _css(), breite=breite, hoehe=900)
    try:
        m = page.evaluate(DESKTOP_MESSEN)
    finally:
        ctx.close()
    assert m["pillen"] == 7 and m["zeilen"] == 1 and m["marke"], m
    assert not m["knopf"] and not m["link"], m
    assert not m["blatt"], m  # mit popover-Unterstuetzung bleibt das Blatt zu


def test_desktop_ohne_popover_der_abschnitt_alle_raeume_steht_am_ende(seite_laden):
    # Browser ohne popover: Attribut inert, :popover-open unbekannt -> sichtbarer Abschnitt;
    # am Desktop erreicht man die Raeume ueber die Pillen, am Handy ueber den Link darauf.
    seite = _seite().replace(" popover aria-labelledby", " aria-labelledby")
    for breite in (1440, 390):
        ctx, page = seite_laden(
            seite, _css(fallback_simulieren=True), breite=breite, hoehe=900
        )
        try:
            m = page.evaluate(DESKTOP_MESSEN)
            if breite == 390:
                page.click(".mn-masthead__raum-link")
                im_bild = page.evaluate(
                    "(() => { const r = document.querySelector('#raumplan').getBoundingClientRect();"
                    " return r.top >= 0 && r.top < window.innerHeight; })()"
                )
        finally:
            ctx.close()
        assert m["blatt"], (breite, m)
        assert not m["knopf"], (breite, m)
        if breite == 1440:
            assert m["pillen"] == 7 and not m["link"], m
        else:
            assert m["link"] and im_bild, (m, im_bild)
