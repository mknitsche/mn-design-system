"""render_font_face 0.24.0: Fingerprints (`dateien`) und Filter (`nur`), additiv (Plan T6, K1)."""

from __future__ import annotations

import re

import pytest
from golden.faelle import pruefe_praefix

from mn_design_system.components.web import WEB_SCHRIFTEN, render_font_face

REGULAR = "Geist-Regular.woff2"
ITALIC = "SourceSerif4-Italic.woff2"


def _urls(css: str) -> list[str]:
    return re.findall(r'url\("([^"]+)"\)', css)


def test_font_face_ohne_argumente_wie_0_23_0():
    pruefe_praefix("font_face")


def test_font_face_setzt_fingerprints_ein():
    dateien = {d: d.replace(".woff2", ".abcd1234.woff2") for *_, d in WEB_SCHRIFTEN}
    css = render_font_face("/assets/fonts/", dateien=dateien)
    assert _urls(css) == [f"/assets/fonts/{dateien[d]}" for *_, d in WEB_SCHRIFTEN]
    # Familie, Gewicht, Stil bleiben dieselben
    assert css.count("@font-face") == len(WEB_SCHRIFTEN)
    assert css.count("font-display: swap;") == len(WEB_SCHRIFTEN)


def test_font_face_nur_filtert_und_unbekannter_name_bricht_laut():
    css = render_font_face("/a/", nur={REGULAR, ITALIC})
    assert _urls(css) == [
        f"/a/{REGULAR}",
        f"/a/{ITALIC}",
    ]  # Reihenfolge der Liste, nicht der Menge
    with pytest.raises(KeyError, match="Geist-Gibtsnicht"):
        render_font_face("/a/", nur={REGULAR, "Geist-Gibtsnicht.woff2"})


def test_font_face_nur_leer_ist_kein_filter_aus_versehen():
    # eine leere Auswahl ist leer — kein stiller Rueckfall auf „alle“
    assert render_font_face("/a/", nur=set()) == ""


def test_font_face_fingerprint_fuer_gewaehlte_pflicht_und_unbekannte_schluessel_laut():
    with pytest.raises(KeyError, match=REGULAR):
        render_font_face("/a/", dateien={ITALIC: "x.woff2"}, nur={REGULAR})
    with pytest.raises(KeyError, match="Geist-Gibtsnicht"):
        render_font_face("/a/", dateien={"Geist-Gibtsnicht.woff2": "x.woff2"})


def test_font_face_dateien_und_nur_zusammen():
    css = render_font_face(
        "/assets/",
        dateien={REGULAR: "r.1.woff2", "Geist-Bold.woff2": "b.1.woff2"},
        nur=[REGULAR],
    )
    assert _urls(css) == ["/assets/r.1.woff2"]


def test_font_face_praefix_regeln_bleiben():
    assert _urls(render_font_face("/assets/fonts", nur=[REGULAR])) == [
        f"/assets/fonts/{REGULAR}"
    ]
