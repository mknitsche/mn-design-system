"""Tests fuer die Listenzeile Ordner/Datei (0.20.0, Magazin-Welle 0, Klassenvertrag Spec Anhang C)."""

from __future__ import annotations

import re

import pytest

from mn_design_system.components._patterns.contracts import DateiZeileInput
from mn_design_system.components.web import (
    render_datei_liste_html,
    render_datei_zeile_css,
    render_datei_zeile_html,
)

# Klassenvertrag Anhang C (jede Klasse muss im CSS eine Regel haben).
KLASSEN = [
    "mn-datei-liste",
    "mn-datei-zeile",
    "mn-datei-zeile--ordner",
    "mn-datei-zeile__kennung",
    "mn-datei-zeile__vorschau",
    "mn-datei-zeile__name",
    "mn-datei-zeile__satz",
    "mn-datei-zeile__meta",
    "mn-datei-zeile__meta--groesse",
    "mn-datei-zeile__neu",
    "mn-datei-zeile__aktion",
]


def _ordner(**kw):
    return DateiZeileInput(
        name="Berichte", href="/magazin/dateien/berichte/", art="ordner", **kw
    )


def _datei(**kw):
    return DateiZeileInput(name="plan.pdf", href="/files/plan.pdf", art="datei", **kw)


class TestOrdnerzeile:
    def test_ordnerzeile_ganze_zeile_ist_link_mit_pfeil(self):
        html = render_datei_zeile_html(_ordner(inhalt="3 Dateien"))
        assert "mn-datei-zeile--ordner" in html
        # genau ein Link, auf den Ordner; die Zeile wird per Streckung ganz klickbar
        assert html.count("<a ") == 1
        assert 'href="/magazin/dateien/berichte/"' in html
        assert "›" in html
        assert "3 Dateien" in html
        # Ordner haben keinen Aktionsknopf
        assert "<button" not in html


class TestDateizeile:
    def test_dateizeile_kennung_name_datum_groesse_aktion(self):
        html = render_datei_zeile_html(
            _datei(
                kennung="PDF",
                datum="heute 06:40",
                groesse="1,2 MB",
                aktion_label="Optionen für plan.pdf",
            )
        )
        assert "mn-datei-zeile--ordner" not in html
        assert 'class="mn-datei-zeile__kennung"' in html
        assert ">PDF<" in html
        assert ">plan.pdf</a>" in html
        assert "heute 06:40" in html
        assert "1,2 MB" in html
        assert "mn-datei-zeile__meta--groesse" in html
        assert '<button type="button" class="mn-datei-zeile__aktion"' in html
        assert 'aria-label="Optionen für plan.pdf"' in html

    def test_ohne_aktion_label_kein_knopf(self):
        assert "<button" not in render_datei_zeile_html(_datei(kennung="PDF"))

    def test_vorschau_ersetzt_kennung(self):
        html = render_datei_zeile_html(
            _datei(kennung="PNG", vorschau_src="/api/thumb?p=a.png")
        )
        assert "<img" in html
        assert 'src="/api/thumb?p=a.png"' in html
        assert "mn-datei-zeile__vorschau" in html
        assert "mn-datei-zeile__kennung" not in html
        assert ">PNG<" not in html

    def test_neu_marke_nur_wenn_neu(self):
        assert "mn-datei-zeile__neu" in render_datei_zeile_html(_datei(neu=True))
        assert "mn-datei-zeile__neu" not in render_datei_zeile_html(_datei(neu=False))

    def test_satz_und_etikett_stehen_unter_dem_namen(self):
        html = render_datei_zeile_html(
            _ordner(satz="Diesen Ordner füllt der Morgenlauf.", etikett="sieht: nur du")
        )
        assert "mn-datei-zeile__satz" in html
        assert "Diesen Ordner füllt der Morgenlauf." in html
        assert "sieht: nur du" in html
        assert html.index("berichte/") < html.index("Morgenlauf")


class TestSicherheit:
    def test_alle_texte_maskiert(self):
        boese = "<b>&\"'"
        html = render_datei_zeile_html(
            _datei(
                kennung=boese,
                datum=boese,
                groesse=boese,
                satz=boese,
                etikett=boese,
                aktion_label=boese,
            ).model_copy(update={"name": boese})
        )
        assert "<b>" not in html
        assert "&lt;b&gt;&amp;" in html

    def test_href_und_vorschau_mit_anfuehrungszeichen_brechen_nicht_aus(self):
        html = render_datei_zeile_html(
            DateiZeileInput(
                name="x", href='/a"onmouseover="1', art="datei", vorschau_src='/t"x'
            )
        )
        assert '"onmouseover' not in html
        assert "&quot;" in html

    @pytest.mark.parametrize(
        "href",
        [
            "javascript:alert(1)",
            "data:text/html,x",
            "//evil.example/x",
            "https://x.example/",
            "/a\\b",
            "/a\nb",
        ],
    )
    def test_fremde_ziele_werden_abgewiesen(self, href):
        with pytest.raises(ValueError):
            DateiZeileInput(name="x", href=href, art="datei")
        with pytest.raises(ValueError):
            DateiZeileInput(name="x", href="/ok", art="datei", vorschau_src=href)

    def test_relative_und_interne_ziele_gehen(self):
        for href in ("/magazin/", "2026-10/", "a/b.pdf", "/api/thumb?p=a%20b"):
            assert DateiZeileInput(name="x", href=href, art="datei").href == href

    def test_art_nur_ordner_oder_datei(self):
        with pytest.raises(ValueError):
            DateiZeileInput(name="x", href="/x", art="link")

    def test_extra_felder_verboten(self):
        with pytest.raises(ValueError):
            DateiZeileInput(name="x", href="/x", art="datei", frei="nein")


class TestListe:
    def test_liste_ist_ul_mit_label_und_zeilen_in_reihenfolge(self):
        html = render_datei_liste_html(
            [_ordner(), _datei()], label="Inhalt von briefing"
        )
        assert html.startswith('<ul class="mn-datei-liste"')
        assert 'aria-label="Inhalt von briefing"' in html
        assert html.count("<li ") == 2
        assert html.index("Berichte") < html.index("plan.pdf")

    def test_leere_liste_ist_leer_nicht_kaputt(self):
        html = render_datei_liste_html([], label="x")
        assert html.count("<li") == 0
        assert "<ul" in html

    def test_label_maskiert(self):
        assert "<i>" not in render_datei_liste_html([], label="<i>x")


class TestCss:
    def test_klassenvertrag_vollstaendig(self):
        css = render_datei_zeile_css()
        for klasse in KLASSEN:
            assert re.search(rf"\.{re.escape(klasse)}(?![\w-])", css), klasse

    def test_css_nur_var(self):
        css = render_datei_zeile_css()
        ohne_var = css
        # jede var(...) samt verschachteltem Rueckfall entfernen
        while "var(" in ohne_var:
            ohne_var = re.sub(r"var\([^()]*\)", "", ohne_var)
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b", ohne_var), (
            "Hexfarbe ausserhalb var()"
        )
        assert "rgb" not in ohne_var
        # keine festen Laengen ausserhalb von var() (ausser 0 und Media-Query-Breite)
        ohne_media = re.sub(r"@media \([^)]*\)", "@media", ohne_var)
        assert not re.search(r"(?<![\w.-])\d+(\.\d+)?(px|rem|em)\b", ohne_media), (
            ohne_media
        )

    def test_zweizeilig_unter_bp_mobile(self):
        css = render_datei_zeile_css()
        assert re.search(r"@media \(max-width: 640px\)", css)
        mobil = css[css.index("@media (max-width: 640px)") :]
        assert '"k n a"' in mobil
        assert '"k m a"' in mobil or '"k m a"' in re.sub(r"\s+", " ", mobil)
        # Groesse haengt am Datum und faellt am Telefon weg
        assert re.search(r"mn-datei-zeile__meta--groesse\s*\{\s*display:\s*none", mobil)

    def test_tokens_aus_dem_vertrag(self):
        css = render_datei_zeile_css()
        for token in (
            "--web-touch-target",
            "--web-text-body",
            "--web-text-ui",
            "--web-text-caption",
            "--web-leading-ui",
            "--web-stroke-line",
            "--web-stroke-focus",
            "--web-color-focus-ring",
            "--color-light-border",
            "--color-light-text-muted",
            "--color-light-accent",
            "--color-light-surface-subtle",
            "--font-weight-medium",
            "--font-tracking-wide",
            "--radius-subtle",
            "--space-2",
            "--space-3",
            "--space-4",
            "--space-10",
        ):
            assert f"var({token}" in css, token

    def test_inline_css_haengt_style_an(self):
        assert render_datei_zeile_html(_datei(), inline_css=True).startswith("<style>")
        assert "<style" not in render_datei_zeile_html(_datei())
