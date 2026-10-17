"""KpiCardInput: Polaritaet und absolutes Delta (0.18.0).

Neu und optional: ``richtung`` (welche Bewegung ist gut?), ``delta_wert`` mit
``delta_einheit`` und ``dezimalstellen``. Ohne diese Felder aendert sich nichts —
``test_kpi_card.py`` (Web, PDF) haelt die alten Ausgaben fest.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mn_design_system.components._patterns._zahl import MINUS, NBSP
from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
    KpiWertung,
)


def _karte(**kw) -> KpiCardInput:
    return KpiCardInput(label="Gewicht", value="72,4", **kw)


class TestDefaults:
    def test_neue_felder_haben_neutrale_defaults(self):
        k = _karte()
        assert k.richtung == "hoeher"
        assert k.delta_wert is None
        assert k.delta_einheit == ""
        assert k.dezimalstellen == 1

    def test_alter_aufruf_bleibt_gueltig(self):
        k = KpiCardInput(
            label="DAX",
            value="22.450",
            change_pct=1.25,
            sparkline_values=[1.0, 2.0],
            caption="Stand",
        )
        assert k.trend_direction() == KpiTrendDirection.UP
        assert k.wertung() == KpiWertung.GUT
        assert k.delta_text() is None

    def test_weiter_frozen_und_extra_forbid(self):
        k = _karte()
        with pytest.raises(ValidationError):
            k.richtung = "niedriger"
        with pytest.raises(ValidationError):
            _karte(foo="bar")


class TestValidierung:
    @pytest.mark.parametrize("richtung", ["hoeher", "niedriger", "neutral"])
    def test_gueltige_richtung(self, richtung):
        assert _karte(richtung=richtung).richtung == richtung

    @pytest.mark.parametrize("richtung", ["hoch", "up", "", "Hoeher", None])
    def test_ungueltige_richtung_wird_abgelehnt(self, richtung):
        with pytest.raises(ValidationError):
            _karte(richtung=richtung)

    @pytest.mark.parametrize("stellen", [0, 1, 6])
    def test_dezimalstellen_im_bereich(self, stellen):
        assert _karte(dezimalstellen=stellen).dezimalstellen == stellen

    @pytest.mark.parametrize("stellen", [-1, 7, 1.5])
    def test_dezimalstellen_ausserhalb_wird_abgelehnt(self, stellen):
        with pytest.raises(ValidationError):
            _karte(dezimalstellen=stellen)

    @pytest.mark.parametrize("wert", [float("nan"), float("inf"), float("-inf")])
    def test_delta_wert_nan_und_unendlich_werden_abgelehnt(self, wert):
        with pytest.raises(ValidationError):
            _karte(delta_wert=wert)

    def test_prozent_und_absolutes_delta_zugleich_sind_mehrdeutig(self):
        """Welche Zahl soll die Karte zeigen? Lieber laut als eine still verworfen."""
        with pytest.raises(ValidationError, match="change_pct"):
            _karte(change_pct=1.0, delta_wert=1.0)

    def test_einheit_ohne_delta_wird_abgelehnt(self):
        """Eine Einheit ohne Zahl waere stumm verworfen worden."""
        with pytest.raises(ValidationError, match="delta_wert"):
            _karte(delta_einheit="kg")

    def test_delta_null_ist_ein_gueltiges_delta(self):
        """0.0 ist ein Wert („unveraendert"), nicht „kein Delta"."""
        k = _karte(delta_wert=0.0, delta_einheit="kg")
        assert k.delta_text() == "unverändert"
        assert k.trend_direction() == KpiTrendDirection.NEUTRAL


class TestTrendDirectionMitDelta:
    def test_prozent_unveraendert(self):
        assert _karte(change_pct=0.2).trend_direction() == KpiTrendDirection.NEUTRAL
        assert _karte(change_pct=0.5).trend_direction() == KpiTrendDirection.UP
        assert _karte(change_pct=-0.5).trend_direction() == KpiTrendDirection.DOWN

    def test_delta_richtung_folgt_dem_vorzeichen(self):
        assert _karte(delta_wert=0.8).trend_direction() == KpiTrendDirection.UP
        assert _karte(delta_wert=-0.8).trend_direction() == KpiTrendDirection.DOWN

    def test_delta_auf_null_gerundet_ist_neutral(self):
        assert _karte(delta_wert=0.04).trend_direction() == KpiTrendDirection.NEUTRAL
        assert _karte(delta_wert=-0.04).trend_direction() == KpiTrendDirection.NEUTRAL

    def test_delta_ohne_die_prozent_schwelle(self):
        """Die 0,5-%-Schwelle gehoert dem Prozentwert; ein Delta von 0,1 kg ist
        eine Bewegung, sobald es nach dem Runden nicht null ist."""
        assert _karte(delta_wert=0.1).trend_direction() == KpiTrendDirection.UP

    def test_dezimalstellen_entscheiden_ueber_null(self):
        assert (
            _karte(delta_wert=0.04, dezimalstellen=2).trend_direction()
            == KpiTrendDirection.UP
        )

    def test_richtung_aendert_die_bewegung_nicht(self):
        for richtung in ("hoeher", "niedriger", "neutral"):
            k = _karte(delta_wert=-0.8, richtung=richtung)
            assert k.trend_direction() == KpiTrendDirection.DOWN


class TestWertung:
    @pytest.mark.parametrize(
        ("richtung", "delta", "soll"),
        [
            ("hoeher", 0.8, KpiWertung.GUT),
            ("hoeher", -0.8, KpiWertung.SCHLECHT),
            ("hoeher", 0.0, KpiWertung.NEUTRAL),
            ("niedriger", 0.8, KpiWertung.SCHLECHT),
            ("niedriger", -0.8, KpiWertung.GUT),
            ("niedriger", 0.0, KpiWertung.NEUTRAL),
            ("neutral", 0.8, KpiWertung.NEUTRAL),
            ("neutral", -0.8, KpiWertung.NEUTRAL),
            ("neutral", 0.0, KpiWertung.NEUTRAL),
        ],
    )
    def test_matrix_mit_absolutem_delta(self, richtung, delta, soll):
        assert _karte(delta_wert=delta, richtung=richtung).wertung() == soll

    @pytest.mark.parametrize(
        ("richtung", "pct", "soll"),
        [
            ("hoeher", 2.0, KpiWertung.GUT),
            ("hoeher", -2.0, KpiWertung.SCHLECHT),
            ("niedriger", 2.0, KpiWertung.SCHLECHT),
            ("niedriger", -2.0, KpiWertung.GUT),
            ("niedriger", 0.2, KpiWertung.NEUTRAL),  # unter der 0,5-%-Schwelle
            ("neutral", 2.0, KpiWertung.NEUTRAL),
        ],
    )
    def test_matrix_mit_prozent(self, richtung, pct, soll):
        assert _karte(change_pct=pct, richtung=richtung).wertung() == soll

    def test_ohne_jedes_delta_ist_die_wertung_neutral(self):
        assert _karte(richtung="niedriger").wertung() == KpiWertung.NEUTRAL


class TestDeltaText:
    def test_deutsch_mit_einheit(self):
        assert _karte(delta_wert=-1.2, delta_einheit="kg").delta_text() == (
            f"{MINUS}1,2{NBSP}kg"
        )

    def test_dezimalstellen_und_tausenderpunkt(self):
        k = _karte(delta_wert=1234.567, dezimalstellen=2, delta_einheit="Schritte")
        assert k.delta_text() == f"+1.234,57{NBSP}Schritte"

    def test_ohne_delta_kein_text(self):
        assert _karte(change_pct=1.0).delta_text() is None
