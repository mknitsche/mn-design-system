"""Schriftfamilien: Fett und Kursiv muessen im PDF sichtbar sein (v0.15.0, claudeAI cld1-S112).

Hintergrund: ``register_all_fonts`` meldete jeden Schnitt einzeln an, aber keine Familie.
ReportLab loest ``<b>``/``<i>`` in einem Paragraph ueber die Familien-Zuordnung auf; ohne
sie setzt es den Grundschnitt — Fett und Kursiv waren in allen ReportLab-PDFs der
Konsumenten unsichtbar, ohne Fehler. Fuer Geist fehlte ausserdem der kursive Schnitt.

Geprueft wird die WIRKUNG: welcher Schnitt an einer Auszeichnung tatsaechlich ankommt
(``Paragraph.frags``), nicht ob eine Tabelle einen Eintrag hat.
"""

from __future__ import annotations

import pytest
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from mn_design_system.fonts import FONT_DIR, font_path, register_all_fonts


@pytest.fixture(autouse=True)
def _register_fonts():
    register_all_fonts()


def _schnitte(grundschrift: str) -> dict[str, str]:
    """Welcher Schnitt kommt bei normal / <b> / <i> / <b><i> an?"""
    text = "n <b>f</b> <i>k</i> <b><i>fk</i></b>"
    p = Paragraph(text, ParagraphStyle("t", fontName=grundschrift, fontSize=10))
    ergebnis = {}
    for frag in p.frags:
        wort = frag.text.strip()
        if wort:
            ergebnis[wort] = frag.fontName
    return ergebnis


@pytest.mark.parametrize(
    ("grund", "fett", "kursiv", "fettkursiv"),
    [
        ("Geist", "Geist-Bold", "Geist-Italic", "Geist-BoldItalic"),
        (
            "SourceSerif",
            "SourceSerif-Bold",
            "SourceSerif-Italic",
            "SourceSerif-BoldItalic",
        ),
        ("SourceSans", "SourceSans-Bold", "SourceSans-Italic", "SourceSans-BoldItalic"),
        ("Inter", "Inter-Bold", "Inter-Italic", "Inter-BoldItalic"),
        ("NotoSans", "NotoSans-Bold", "NotoSans-Italic", "NotoSans-BoldItalic"),
    ],
)
def test_auszeichnung_trifft_den_richtigen_schnitt(grund, fett, kursiv, fettkursiv):
    s = _schnitte(grund)
    assert s == {"n": grund, "f": fett, "k": kursiv, "fk": fettkursiv}


def test_geist_kursiv_schnitte_liegen_im_paket():
    for name in ("Geist-Italic", "Geist-MediumItalic", "Geist-BoldItalic"):
        pfad = font_path(name)
        assert pfad is not None, f"{name} nicht im Paket"
        assert pfad.is_file()


def test_geist_lizenztext_liegt_bei():
    """SIL OFL 1.1 verlangt, dass der Lizenztext die Schrift begleitet."""
    lizenz = FONT_DIR / "geist" / "OFL.txt"
    assert lizenz.is_file()
    assert "SIL OPEN FONT LICENSE" in lizenz.read_text(encoding="utf-8").upper()


def test_helvetica_kursiv_bleibt_in_der_grotesk():
    """Die Helvetica-Ersatznamen zeigen auf Geist; ihr Kursiv darf nicht in eine
    Serifenschrift springen (bis 0.14.2: Source Serif Italic)."""
    assert font_path("Helvetica-Oblique") == font_path("Geist-Italic")
    assert font_path("Helvetica-BoldOblique") == font_path("Geist-BoldItalic")
    assert font_path("Arial-Italic") == font_path("Geist-Italic")
    assert font_path("Arial-BoldItalic") == font_path("Geist-BoldItalic")


def test_mono_ohne_kursiv_faellt_auf_aufrecht_zurueck():
    """JetBrains Mono liegt nur aufrecht und fett bei: Fett wirkt, Kursiv bleibt aufrecht
    (Code wird nicht kursiv gesetzt) — bewusst, nicht still."""
    s = _schnitte("JetBrainsMono")
    assert s["f"] == "JetBrainsMono-Bold"
    assert s["k"] == "JetBrainsMono"


def test_jeder_eingetragene_schnitt_existiert():
    """Ein Eintrag ohne Datei wird beim Registrieren still uebersprungen und faellt erst
    beim Rendern als ValueError auf (bis 0.14.2: STIXTwo-BoldItalic)."""
    from mn_design_system import fonts

    fehlend = [name for name in fonts._FONT_MAP if font_path(name) is None]
    assert fehlend == []


def test_zitat_token_ist_ein_angemeldeter_schriftname():
    """Bis 0.14.2 lieferte font_family("italic-editorial") "SourceSerif4-Italic", angemeldet
    war die Datei nur als "SourceSerif-Italic" — wer den Token nahm, bekam beim Rendern
    einen ValueError (claudeAI bibel_block umging das seit v0.5.0 mit einem Literal)."""
    from reportlab.pdfbase import pdfmetrics

    from mn_design_system.helpers import font_family

    for token in ("sans", "italic-editorial", "italic-ui", "mono", "table-default"):
        assert pdfmetrics.getFont(font_family(token)) is not None, token


def test_kursiv_ui_ist_kursiv_und_bleibt_in_der_grotesk():
    from mn_design_system.helpers import font_family

    assert font_family("italic-ui") == "Geist-MediumItalic"


# --- Web: die Schriften kommen aus dem Design-System, nicht aus dem Konsumenten --------


def test_web_schriften_liegen_im_paket_und_decken_die_font_face_ab():
    from mn_design_system.components.web.foundation import (
        WEB_SCHRIFTEN,
        render_font_face,
        web_font_dir,
    )

    css = render_font_face("/assets/fonts/")
    for familie, gewicht, stil, datei in WEB_SCHRIFTEN:
        assert (web_font_dir() / datei).is_file(), datei
        assert f'url("/assets/fonts/{datei}")' in css
    assert css.count("@font-face") == len(WEB_SCHRIFTEN)


def test_web_geist_hat_echte_kursiv_schnitte():
    """Ohne kursiven @font-face schraegt der Browser Geist kuenstlich an (Lade-Chips,
    KPI-Bildunterschriften bis 0.14.2)."""
    from mn_design_system.components.web.foundation import WEB_SCHRIFTEN

    geist_kursiv = {g for f, g, s, _ in WEB_SCHRIFTEN if f == "Geist" and s == "italic"}
    assert geist_kursiv == {"400", "500", "700"}
