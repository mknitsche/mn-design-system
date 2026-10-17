"""Deutsches Zahlenformat (intern, ``components/_patterns/_zahl.py``, 0.17.1).

Eine Stelle fuer Dezimalkomma, Tausenderpunkt, Minuszeichen U+2212 und die Frage
„rundet das auf null?" — der Verlauf-Chart und die KPI-Karte brauchen dasselbe.
"""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns._zahl import (
    MINUS,
    NBSP,
    delta_de,
    rundet_auf_null,
    zahl_de,
    zahl_de_kurz,
)


class TestZahlDe:
    """Unveraendert aus 0.17.0 (vorher in ``_verlauf.py``)."""

    @pytest.mark.parametrize(
        ("wert", "stellen", "soll"),
        [
            (1234.5, 1, "1.234,5"),
            (999.9, 1, "999,9"),
            (1000, 0, "1.000"),
            (-72.45, 2, "-72,45"),
            (70.0, 1, "70,0"),
            (0, 0, "0"),
        ],
    )
    def test_formate(self, wert, stellen, soll):
        assert zahl_de(wert, stellen) == soll


class TestZahlDeKurz:
    """Zielband-Beschriftung: „70–74 kg" statt „70,0–74,0 kg"."""

    @pytest.mark.parametrize(
        ("wert", "stellen", "soll"),
        [
            (70.0, 1, "70"),
            (74.0, 1, "74"),
            (72.5, 1, "72,5"),
            (72.0, 2, "72"),
            (72.5, 2, "72,5"),
            (72.55, 2, "72,55"),
            (100.0, 1, "100"),  # die Null VOR dem Komma bleibt
            (1000.0, 1, "1.000"),
            (1234.5, 1, "1.234,5"),
            (1000.0, 0, "1.000"),  # ohne Dezimalstellen gibt es nichts zu kuerzen
            (100.0, 0, "100"),
            (0.0, 1, "0"),
            (-5.0, 1, "-5"),
        ],
    )
    def test_ohne_ueberfluessige_nullen(self, wert, stellen, soll):
        assert zahl_de_kurz(wert, stellen) == soll

    def test_minus_null_wird_null(self):
        """-0,04 auf eine Stelle ist „0", nicht „-0"."""
        assert zahl_de_kurz(-0.04, 1) == "0"


class TestRundetAufNull:
    @pytest.mark.parametrize(
        ("wert", "stellen", "soll"),
        [
            (0.0, 1, True),
            (-0.0, 1, True),
            (0.04, 1, True),
            (-0.04, 1, True),
            (0.049, 1, True),
            (0.06, 1, False),
            (-0.06, 1, False),
            (0.4, 0, True),
            (0.6, 0, False),
            (0.004, 2, True),
            (0.006, 2, False),
        ],
    )
    def test_faelle(self, wert, stellen, soll):
        assert rundet_auf_null(wert, stellen) is soll


class TestDeltaDe:
    def test_positiv_mit_plus_und_einheit(self):
        assert delta_de(1.23, 1, "kg") == f"+1,2{NBSP}kg"

    def test_negativ_mit_echtem_minuszeichen(self):
        text = delta_de(-1.2, 1, "kg")
        assert text == f"{MINUS}1,2{NBSP}kg"
        assert MINUS == "\u2212"
        assert "-" not in text  # kein Bindestrich-Minus

    def test_einheit_haengt_hinter_einem_geschuetzten_leerzeichen(self):
        """U+00A0, nicht U+0020: zwischen Zahl und Einheit bricht keine Zeile um."""
        assert NBSP == "\u00a0"
        assert delta_de(2.0, 0, "h") == "+2\u00a0h"

    def test_ohne_einheit_kein_leerzeichen_am_ende(self):
        assert delta_de(3.0, 0) == "+3"
        assert delta_de(-3.0, 0) == f"{MINUS}3"

    def test_tausenderpunkt_ab_1000(self):
        assert delta_de(999.9, 1) == "+999,9"
        assert delta_de(1000, 0) == "+1.000"
        assert delta_de(-1234567.891, 2, "m") == f"{MINUS}1.234.567,89{NBSP}m"

    def test_dezimalstellen_werden_gehalten(self):
        assert delta_de(2.0, 2, "kg") == f"+2,00{NBSP}kg"
        assert delta_de(2.0, 0, "kg") == f"+2{NBSP}kg"

    @pytest.mark.parametrize("wert", [0.0, -0.0, 0.04, -0.04, 0.049])
    def test_auf_null_gerundet_ist_unveraendert(self, wert):
        """Weder „+0,0 kg" noch „−0,0 kg": eine Messung, die sich nicht bewegt hat."""
        assert delta_de(wert, 1, "kg") == "unverändert"

    def test_unveraendert_ohne_einheit_und_vorzeichen(self):
        text = delta_de(-0.01, 1, "kg")
        assert text == "unverändert"
        assert "kg" not in text and MINUS not in text and "+" not in text

    def test_kaufmaennisch_gerundet_auch_auf_dem_halbwert(self):
        """2,5 → 3 und 0,25 → 0,3 (nicht 2 und 0,2 wie beim Rundungsmodus von
        ``format``): das Delta ist eine Zahl, die ein Mensch liest."""
        assert delta_de(2.5, 0) == "+3"
        assert delta_de(-2.5, 0) == f"{MINUS}3"
        assert delta_de(0.25, 1) == "+0,3"
        assert delta_de(0.35, 1) == "+0,4"  # 0.35 ist binaer 0.34999…
