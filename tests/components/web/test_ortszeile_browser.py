"""Ortszeile im echten Browser (0.24.0): einzeilig, vorn gekuerzt, das letzte Glied voll sichtbar."""

from __future__ import annotations

from mn_design_system.components._patterns.contracts import OrtszeileInput
from mn_design_system.components.web import (
    render_foundation_css,
    render_ortszeile_css,
    render_ortszeile_html,
)

LANG = OrtszeileInput(
    glieder=(
        ("Observatorium und alles, was dazugehoert", "/observatorium/"),
        ("Gesundheit und Vitalitaet im Ueberblick", "/observatorium/gesundheit/"),
        ("Schlaf", "/observatorium/gesundheit/schlaf/"),
    )
)


def _messe(seite_laden, breite: int):
    ctx, page = seite_laden(
        render_ortszeile_html(LANG),
        render_foundation_css() + render_ortszeile_css(),
        breite=breite,
    )
    try:
        return page.evaluate(
            """() => {
              const ol = document.querySelector('.mn-ortszeile ol');
              const lis = [...ol.children];
              const r = (e) => e.getBoundingClientRect();
              const letztes = document.querySelector('.mn-ortszeile__eltern');
              return {
                zeilen: new Set(lis.map((l) => Math.round(r(l).top))).size,
                olBreite: r(ol).width,
                letztesVoll: letztes.scrollWidth <= letztes.clientWidth + 1,
                letztesRechts: r(lis[lis.length - 1]).right <= r(ol).right + 1,
                vorneGekuerzt: lis[0].firstElementChild.scrollWidth > lis[0].firstElementChild.clientWidth,
                hoehe: r(letztes).height,
              };
            }"""
        )
    finally:
        ctx.close()


def test_schmal_einzeilig_vorn_gekuerzt_letztes_voll(seite_laden):
    m = _messe(seite_laden, 390)
    assert m["zeilen"] == 1, m
    assert m["letztesVoll"], m
    assert m["letztesRechts"], m
    assert m["vorneGekuerzt"], m
    assert m["hoehe"] >= 44, m  # Ziel: Navigation >= 44 px (touch-target)


def test_breit_nichts_gekuerzt(seite_laden):
    m = _messe(seite_laden, 1400)
    assert m["zeilen"] == 1, m
    assert not m["vorneGekuerzt"], m


def test_kuerzt_von_links_das_vorletzte_glied_bleibt_voll(seite_laden):
    # Erstes Glied sehr lang, die uebrigen kurz: es reicht, das erste zu kuerzen.
    kette = OrtszeileInput(
        glieder=(
            (
                "Observatorium und alles, was dazugehoert, ausfuehrlich beschrieben",
                "/o/",
            ),
            ("Projekte", "/o/p/"),
            ("Gesundheit", "/o/p/g/"),
            ("Schlaf", "/o/p/g/s/"),
        )
    )
    for breite in (320, 360, 390):
        ctx, page = seite_laden(
            render_ortszeile_html(kette),
            render_foundation_css() + render_ortszeile_css(),
            breite=breite,
        )
        try:
            m = page.evaluate(
                """() => [...document.querySelectorAll('.mn-ortszeile li > a')]
                  .map((a) => [a.scrollWidth > a.clientWidth, Math.round(a.clientWidth)])"""
            )
        finally:
            ctx.close()
        gekuerzt = [g for g, _ in m]
        assert gekuerzt == [True, False, False, False], (breite, m)


def test_erstes_glied_bleibt_als_auslassung_sichtbar(seite_laden):
    kette = OrtszeileInput(
        glieder=(
            ("Atelier", "/a/"),
            ("Projekte", "/a/p/"),
            ("My Way to Marathon", "/a/p/m/"),
            ("Tagebuch", "/a/p/m/t/"),
        )
    )
    for breite in (320, 360, 390):
        ctx, page = seite_laden(
            render_ortszeile_html(kette),
            render_foundation_css() + render_ortszeile_css(),
            breite=breite,
        )
        try:
            m = page.evaluate(
                """() => {
                  const a = document.querySelector('.mn-ortszeile li:first-child > a');
                  return {breite: a.clientWidth, schrift: parseFloat(getComputedStyle(a).fontSize),
                          gekuerzt: a.scrollWidth > a.clientWidth};
                }"""
            )
        finally:
            ctx.close()
        # nie 0 px: mindestens 1em, sonst bliebe ein Link ohne sichtbare „…“
        assert m["breite"] >= m["schrift"], (breite, m)
