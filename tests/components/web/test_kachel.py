"""Kachel, Status-Punkt, Fortschritt (0.24.0, Welle 1, Plan T6)."""

from __future__ import annotations

import re

import pytest
from golden.faelle import pruefe_praefix
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    FortschrittInput,
    KachelInput,
    StatusPunktInput,
)
from mn_design_system.components.web import (
    render_fortschritt_css,
    render_fortschritt_html,
    render_kachel_css,
    render_kachel_html,
    render_status_punkt_css,
    render_status_punkt_html,
)
from mn_design_system.tokens import get


def _ohne_var(css: str) -> str:
    css = re.sub(r"@media \([^)]*\)", "", css)
    css = re.sub(r"rgba\([^()]*\)", "", css)
    while "var(" in css:
        css = re.sub(r"var\([^()]*\)", "", css)
    return css


def _kein_rohwert(css: str) -> None:
    ohne = _ohne_var(css)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne), ohne
    assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne), ohne


def test_alte_eingaben_rendern_wie_0_23_0():
    # die KPI-Karte und die Content-Karte bleiben, wie sie waren
    pruefe_praefix("kpi_card")
    pruefe_praefix("card_grid")


class TestKachel:
    def test_struktur(self):
        html = render_kachel_html(
            KachelInput(
                kicker="Aufgaben",
                titel_id="k-aufgaben",
                aussage="Drei Aufgaben sind fällig.",
                zahl="12",
                link=("Alle Aufgaben", "/atelier/aufgaben/"),
                stand="Aktualisiert 14.11. 06:05",
                status=StatusPunktInput(stufe="ok", wort="alles gut"),
            )
        )
        assert html.startswith(
            '<section class="mn-kachel" aria-labelledby="k-aufgaben">'
        )
        assert '<h3 id="k-aufgaben" class="mn-kachel__kicker">Aufgaben</h3>' in html
        assert '<p class="mn-kachel__zahl">12</p>' in html
        assert '<p class="mn-kachel__aussage">Drei Aufgaben sind fällig.</p>' in html
        assert (
            '<a class="mn-kachel__link" href="/atelier/aufgaben/">Alle Aufgaben</a>'
            in html
        )
        assert '<p class="mn-kachel__stand">Aktualisiert 14.11. 06:05</p>' in html
        assert 'class="mn-status mn-status--ok"' in html

    def test_kachel_ohne_zahl_zeigt_keine(self):
        html = render_kachel_html(
            KachelInput(kicker="K", titel_id="k", aussage="Satz.", link=("Mehr", "/x/"))
        )
        for fehlt in ("mn-kachel__zahl", "mn-kachel__stand", "mn-status"):
            assert fehlt not in html

    def test_kachel_hat_kein_freies_html(self):
        # strenge Kachel: kein inhalt_html, kein fuss_link, kein display_zahl mehr
        felder = set(KachelInput.model_fields)
        assert felder == {
            "kicker",
            "aussage",
            "link",
            "titel_id",
            "zahl",
            "stand",
            "status",
        }
        with pytest.raises(ValidationError):
            KachelInput(
                kicker="K",
                titel_id="k",
                aussage="a",
                link=("x", "/x/"),
                inhalt_html="<b>x</b>",
            )
        # alles, was hineingegeben wird, kommt maskiert heraus
        html = render_kachel_html(
            KachelInput(
                kicker="<b>K</b>",
                titel_id="k",
                aussage="<i>a</i>",
                zahl="<u>1</u>",
                link=("<s>mehr</s>", "/x/"),
                stand="<em>stand</em>",
                status=StatusPunktInput(stufe="ok", wort="<q>w</q>"),
            )
        )
        for roh in ("<b>", "<i>", "<u>", "<s>", "<em>", "<q>"):
            assert roh not in html
        assert "&lt;b&gt;K&lt;/b&gt;" in html

    def test_kachel_genau_ein_link_und_nur_intern(self):
        html = render_kachel_html(
            KachelInput(
                kicker="K", titel_id="k", aussage="a", link=("Mehr", "/x/?a=1#b")
            )
        )
        assert html.count("<a ") == 1 and html.count("href=") == 1
        # die ganze Kachel ist das Ziel: Pseudo-Element des einen Links, kein zweiter Link
        css = render_kachel_css()
        assert re.search(r"\.mn-kachel__link::after\s*\{[^}]*position:\s*absolute", css)
        assert re.search(r"\.mn-kachel\s*\{[^}]*position:\s*relative", css)
        for href in (
            "javascript:x",
            "//evil.example/",
            "https://x.example/",
            "x/relativ/",
            "/\\host",
            "/a\tb",
            "",
            "#anker",
        ):
            with pytest.raises(ValidationError):
                KachelInput(kicker="K", titel_id="k", aussage="a", link=("x", href))

    @pytest.mark.parametrize("titel_id", ["", "1a", "a b", 'a"b', "a>b"])
    def test_titel_id_muss_ein_id_sein(self, titel_id):
        with pytest.raises(ValidationError):
            KachelInput(kicker="K", titel_id=titel_id, aussage="a", link=("x", "/x/"))

    def test_aussage_und_link_sind_pflicht(self):
        with pytest.raises(ValidationError):
            KachelInput(kicker="K", titel_id="k", link=("x", "/x/"))
        with pytest.raises(ValidationError):
            KachelInput(kicker="K", titel_id="k", aussage="a")
        with pytest.raises(ValidationError):
            KachelInput(kicker="K", titel_id="k", aussage=" ", link=("x", "/x/"))

    def test_raster_zwei_spalten_ab_bp_tablet_darunter_eine(self):
        css = render_kachel_css()
        assert ".mn-kachel-raster" in css
        vor_media = css.split("@media", 1)[0]
        assert re.search(
            r"\.mn-kachel-raster\s*\{[^}]*grid-template-columns:\s*minmax\(0, 1fr\)",
            vor_media,
        )
        unter = css.split("@media", 1)[1]
        assert f"min-width: {get('web.layout.bp-tablet')}" in unter
        assert "repeat(2," in unter
        assert "900px" not in css  # das feste Mass der heutigen Startseite

    def test_css_kein_rohwert(self):
        _kein_rohwert(render_kachel_css())

    def test_inline_css(self):
        k = KachelInput(kicker="K", titel_id="k", aussage="a", link=("x", "/x/"))
        assert render_kachel_html(k, inline_css=True).startswith("<style>")
        assert "<style" not in render_kachel_html(k)


class TestStatusPunkt:
    @pytest.mark.parametrize("stufe", ["ok", "warn", "alarm", "unbekannt"])
    def test_symbol_und_wort_nie_farbe_allein(self, stufe):
        html = render_status_punkt_html(StatusPunktInput(stufe=stufe, wort="alles gut"))
        assert f'class="mn-status mn-status--{stufe}"' in html
        assert '<span class="mn-status__wort">alles gut</span>' in html
        symbol = re.search(
            r'<span class="mn-status__symbol" aria-hidden="true">(.+?)</span>', html
        )
        assert symbol and symbol.group(1).strip()

    def test_symbole_unterscheiden_sich_je_stufe(self):
        symbole = {
            s: re.search(
                r'__symbol" aria-hidden="true">(.+?)</span>',
                render_status_punkt_html(StatusPunktInput(stufe=s, wort="w")),
            ).group(1)
            for s in ("ok", "warn", "alarm", "unbekannt")
        }
        assert len(set(symbole.values())) == 4, symbole

    def test_wort_maskiert_und_pflicht(self):
        assert "&lt;b&gt;" in render_status_punkt_html(
            StatusPunktInput(stufe="ok", wort="<b>")
        )
        with pytest.raises(ValidationError):
            StatusPunktInput(stufe="ok", wort="")

    def test_unbekannte_stufe_wird_abgewiesen(self):
        with pytest.raises(ValidationError):
            StatusPunktInput(stufe="gelb", wort="w")

    def test_css_kein_rohwert_und_aus_status_tokens(self):
        css = render_status_punkt_css()
        _kein_rohwert(css)
        for token in (
            "--color-status-success",
            "--color-status-error",
            "--color-status-urgent",
        ):
            assert f"var({token}" in css


class TestFortschritt:
    def test_progressbar_mit_aria_valuenow(self):
        html = render_fortschritt_html(
            FortschrittInput(anteil=0.375, label="Woche", label_id="f1")
        )
        assert 'role="progressbar"' in html
        assert 'aria-valuemin="0"' in html and 'aria-valuemax="100"' in html
        assert 'aria-valuenow="38"' in html
        assert 'aria-labelledby="f1"' in html
        assert '<span id="f1" class="mn-fortschritt__label">Woche</span>' in html
        assert "aria-label=" not in html  # kein doppelter Name

    @pytest.mark.parametrize("anteil", [0, 0.0, 1, 1.0])
    def test_grenzen_sind_erlaubt(self, anteil):
        render_fortschritt_html(
            FortschrittInput(anteil=anteil, label="x", label_id="f1")
        )

    @pytest.mark.parametrize("anteil", [-0.01, 1.01, 2, float("nan")])
    def test_ausserhalb_null_bis_eins_wird_abgewiesen(self, anteil):
        with pytest.raises(ValidationError):
            FortschrittInput(anteil=anteil, label="x", label_id="f1")

    def test_fuellung_ohne_inline_style(self):
        # die Seite darf eine CSP ohne style-src 'unsafe-inline' haben: Breite als SVG-Mass
        html = render_fortschritt_html(
            FortschrittInput(anteil=0.25, label="x", label_id="f1")
        )
        assert "style=" not in html
        assert re.search(r'<rect class="mn-fortschritt__fuellung"[^>]*width="25"', html)

    def test_label_maskiert(self):
        html = render_fortschritt_html(
            FortschrittInput(anteil=0.5, label='<b>"x"', label_id="f1")
        )
        assert "<b>" not in html

    def test_css_kein_rohwert(self):
        _kein_rohwert(render_fortschritt_css())


def test_link_vertauscht_faellt_auf():
    with pytest.raises(ValidationError, match="sieht wie ein Ziel aus"):
        KachelInput(kicker="K", titel_id="k", aussage="a", link=("/x/", "/mehr/"))


def test_fortschritt_label_id_muss_eine_id_sein():
    for kaputt in ("", "1a", 'a"b'):
        with pytest.raises(ValidationError):
            FortschrittInput(anteil=0.5, label="x", label_id=kaputt)
