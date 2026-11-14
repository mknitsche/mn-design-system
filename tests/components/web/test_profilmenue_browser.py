"""Profil-Knopf, Profil-Menue und Schema-Skript im echten Browser (0.24.0, Plan T24)."""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns.contracts import (
    MastheadChip,
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    ProfilMenueInput,
    WebTier,
)
from mn_design_system.components.web import (
    LOGO_KOPF_DATEI,
    logos_dir,
    render_font_face,
    render_foundation_css,
    render_masthead_css,
    render_masthead_html,
    render_profilmenue_css,
    render_profilmenue_html,
    render_schema_js,
    web_font_dir,
)

_LOGO = (logos_dir() / LOGO_KOPF_DATEI).as_uri()
_PROFIL = ProfilMenueInput(profil_href="/start/profil/")


def _kopf(form: str) -> str:
    kompakt = {"form": "kompakt", "blicke": 2, "raum_schalter": "Atelier"}
    return render_masthead_html(
        MastheadInput(
            emblem=MastheadEmblem(src=_LOGO, alt="MKN", href="/start/"),
            wordmark="MKN 2nd Brain",
            edition_date="Samstag, 14. November",
            tier_items=[
                MastheadTierItem(
                    label=l, href=f"/{l.lower()}/", tier=t, active=l == "Atelier"
                )
                for l, t in (
                    ("Start", WebTier.START),
                    ("Heute", WebTier.START),
                    ("Atelier", WebTier.ATELIER),
                )
            ],
            context_chip=MastheadChip(tier=WebTier.ATELIER, label="Atelier · GREEN"),
            profil=_PROFIL,
            **(kompakt if form == "kompakt" else {}),
        )
    )


def _css(fallback: bool = False) -> str:
    css = (
        render_font_face(web_font_dir().as_uri() + "/")
        + render_foundation_css()
        + render_masthead_css(kompakt=True)
        + render_profilmenue_css()
    )
    if fallback:  # ein Browser ohne :popover-open: dieselbe Seite, dieselben Regeln
        css = css.replace(
            "@supports selector(:popover-open)", "@supports selector(:kein-solcher)"
        )
    return css


def _seite(form: str) -> str:
    return _kopf(form) + "<main><p>Inhalt</p></main>" + render_profilmenue_html(_PROFIL)


SICHTBAR = """(s) => { const e = document.querySelector(s);
  return !!e && getComputedStyle(e).display !== 'none'; }"""
OFFEN = "document.querySelector('#profilmenue').matches(':popover-open')"


def test_profil_knopf_handy_sichtbar_chip_verborgen(seite_laden):
    ctx, page = seite_laden(_seite("kompakt"), _css(), breite=390, hoehe=844)
    try:
        assert page.evaluate(SICHTBAR, ".mn-masthead__profil")
        assert not page.evaluate(SICHTBAR, ".mn-masthead__profil-link")
        assert not page.evaluate(SICHTBAR, ".mn-masthead__chip")
        m = page.evaluate(
            """() => { const b = document.querySelector('.mn-masthead__profil')
              .getBoundingClientRect();
              return {h: b.height, w: b.width, rechts: b.right <= window.innerWidth,
                      breiter: document.documentElement.scrollWidth > window.innerWidth}; }"""
        )
        assert m["h"] >= 44 and m["w"] >= 44 and m["rechts"] and not m["breiter"], m
    finally:
        ctx.close()


def test_rechner_chip_bleibt_und_profil_knopf_steht_daneben(seite_laden):
    ctx, page = seite_laden(_seite("kompakt"), _css(), breite=1400, hoehe=844)
    try:
        assert page.evaluate(SICHTBAR, ".mn-masthead__chip")
        assert page.evaluate(SICHTBAR, ".mn-masthead__profil")
    finally:
        ctx.close()


def test_profilmenue_oeffnet_drei_zustaende_esc_schliesst(seite_laden):
    ctx, page = seite_laden(_seite("kompakt"), _css(), breite=390, hoehe=844)
    try:
        assert not page.evaluate(SICHTBAR, "#profilmenue")
        page.click(".mn-masthead__profil")
        assert page.evaluate(OFFEN)
        m = page.evaluate(
            """() => { const b = document.querySelector('#profilmenue')
              .getBoundingClientRect();
              return {innen: b.left >= 0 && b.right <= window.innerWidth && b.top >= 0
                      && b.bottom <= window.innerHeight,
                      knoepfe: document.querySelectorAll('[data-schema-wahl]').length,
                      link: document.querySelector('.mn-profilmenue__link').getAttribute('href')}; }"""
        )
        assert m == {"innen": True, "knoepfe": 3, "link": "/start/profil/"}, m
        page.keyboard.press("Escape")
        assert not page.evaluate(OFFEN)
        assert page.evaluate(
            "document.activeElement.classList.contains('mn-masthead__profil')"
        )
    finally:
        ctx.close()


def test_profilmenue_rueckfall_ohne_popover(seite_laden):
    ctx, page = seite_laden(_seite("kompakt"), _css(True), breite=390, hoehe=844)
    try:
        assert page.evaluate(SICHTBAR, ".mn-masthead__profil-link")
        assert not page.evaluate(SICHTBAR, ".mn-masthead__profil")
        assert page.evaluate(SICHTBAR, "#profilmenue")  # nie unerreichbar
        page.click(".mn-masthead__profil-link")
        assert page.evaluate("location.hash") == "#profilmenue"
    finally:
        ctx.close()


def _schema_seite(tmp_path) -> str:
    """Eine Seite mit dem Schema-Skript im <head>; sie notiert `data-schema` beim Lauf des
    naechsten Skripts (vor dem ersten Zeichnen) und bei DOMContentLoaded."""
    html = (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        f"<script>{render_schema_js()}</script>"
        "<script>window.__sofort = document.documentElement.getAttribute('data-schema');"
        "document.addEventListener('DOMContentLoaded', function () {"
        "window.__dcl = document.documentElement.getAttribute('data-schema'); });</script>"
        f"<style>{_css()}</style></head><body>{_seite('kompakt')}</body></html>"
    )
    datei = tmp_path / "schema.html"
    datei.write_text(html, encoding="utf-8")
    return datei.as_uri()


def test_schema_js_setzt_data_schema_vor_dem_ersten_zeichnen(browser, tmp_path):
    url = _schema_seite(tmp_path)
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    ctx.add_init_script("window.localStorage.setItem('mn-schema', 'dunkel')")
    page = ctx.new_page()
    try:
        page.goto(url)
        # synchron im <head>, vor Body und erstem Zeichnen
        assert page.evaluate("window.__sofort") == "dunkel"
        assert page.evaluate("window.__dcl") == "dunkel"
        assert page.evaluate("document.documentElement.dataset.schema") == "dunkel"
    finally:
        ctx.close()


@pytest.mark.parametrize(
    ("gespeichert", "system", "erwartet"),
    [
        (None, "dark", "dunkel"),  # ohne Wahl folgt es der Systemeinstellung
        (None, "light", None),
        ("auto", "dark", "dunkel"),
        ("hell", "dark", "hell"),  # ausdrueckliche Wahl schlaegt das System
        ("dunkel", "light", "dunkel"),
        ("kaputt", "light", None),  # ungueltiger Wert gilt als auto
    ],
)
def test_schema_js_wahl_und_system(browser, tmp_path, gespeichert, system, erwartet):
    url = _schema_seite(tmp_path)
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844}, color_scheme=system
    )
    if gespeichert is not None:
        ctx.add_init_script(
            f"window.localStorage.setItem('mn-schema', '{gespeichert}')"
        )
    page = ctx.new_page()
    try:
        page.goto(url)
        assert page.evaluate("window.__sofort") == erwartet
    finally:
        ctx.close()


def test_schema_js_bedient_die_drei_knoepfe(browser, tmp_path):
    url = _schema_seite(tmp_path)
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844}, color_scheme="light"
    )
    page = ctx.new_page()
    try:
        page.goto(url)
        pressed = (
            "[...document.querySelectorAll('[data-schema-wahl]')]"
            ".map((b) => b.getAttribute('aria-pressed')).join()"
        )
        assert page.evaluate(pressed) == "true,false,false"
        page.click(".mn-masthead__profil")
        for wahl, attr, knoepfe in (
            ("dunkel", "dunkel", "false,false,true"),
            ("hell", "hell", "false,true,false"),
            ("auto", None, "true,false,false"),
        ):
            page.click(f"[data-schema-wahl={wahl}]")
            assert (
                page.evaluate("document.documentElement.dataset.schema ?? null") == attr
            )
            assert page.evaluate(pressed) == knoepfe
            assert page.evaluate("localStorage.getItem('mn-schema')") == wahl
    finally:
        ctx.close()
