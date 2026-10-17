"""TDD-Tests fuer KPI-Card PDF-Implementierung (Welle B v0.2.0)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Paragraph, Spacer

from mn_design_system.components._patterns._zahl import MINUS, NBSP
from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
)
from mn_design_system.components.pdf.kpi_card import build_kpi_card

# ---------------------------------------------------------------------------
# Contract-Validation
# ---------------------------------------------------------------------------


class TestKpiCardContract:
    def test_minimal_valid(self):
        inp = KpiCardInput(label="DAX", value="22.450")
        assert inp.change_pct is None
        assert inp.sparkline_values is None

    def test_all_fields(self):
        inp = KpiCardInput(
            label="Bitcoin",
            value="75.991,58",
            change_pct=-0.43,
            sparkline_values=[1.0, 2.0, 3.0],
            caption="Stand: 04:50",
        )
        assert inp.change_pct == -0.43

    def test_label_required(self):
        with pytest.raises(ValidationError):
            KpiCardInput(label="", value="100")

    def test_value_required(self):
        with pytest.raises(ValidationError):
            KpiCardInput(label="DAX", value="")

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            KpiCardInput(label="DAX", value="100", foo="bar")


# ---------------------------------------------------------------------------
# Trend-Direction-Helper
# ---------------------------------------------------------------------------


class TestTrendDirection:
    def test_up(self):
        inp = KpiCardInput(label="X", value="1", change_pct=2.5)
        assert inp.trend_direction() == KpiTrendDirection.UP

    def test_down(self):
        inp = KpiCardInput(label="X", value="1", change_pct=-2.5)
        assert inp.trend_direction() == KpiTrendDirection.DOWN

    def test_neutral_zero(self):
        inp = KpiCardInput(label="X", value="1", change_pct=0.0)
        assert inp.trend_direction() == KpiTrendDirection.NEUTRAL

    def test_neutral_none(self):
        inp = KpiCardInput(label="X", value="1", change_pct=None)
        assert inp.trend_direction() == KpiTrendDirection.NEUTRAL

    def test_neutral_micro(self):
        """abs(change) < 0.01 → NEUTRAL (kein UP/DOWN bei Mikro-Bewegung)."""
        inp = KpiCardInput(label="X", value="1", change_pct=0.005)
        assert inp.trend_direction() == KpiTrendDirection.NEUTRAL


# ---------------------------------------------------------------------------
# Build-Output
# ---------------------------------------------------------------------------


class TestBuildKpiCard:
    def test_returns_5_flowables(self):
        """Card hat 5 Flowables: label, value, change, sparkline, caption."""
        inp = KpiCardInput(label="DAX", value="22.450")
        result = build_kpi_card(inp)
        assert len(result) == 5

    def test_label_paragraph(self):
        inp = KpiCardInput(label="Bitcoin", value="75.991")
        result = build_kpi_card(inp)
        assert isinstance(result[0], Paragraph)
        assert result[0].text == "Bitcoin"

    def test_value_paragraph(self):
        inp = KpiCardInput(label="DAX", value="22.450,12")
        result = build_kpi_card(inp)
        assert isinstance(result[1], Paragraph)
        assert "22.450,12" in result[1].text

    def test_change_positive(self):
        inp = KpiCardInput(label="X", value="100", change_pct=1.25)
        result = build_kpi_card(inp)
        change_text = result[2].text
        assert "▲" in change_text
        assert "+1,25%" in change_text  # deutsche Notation

    def test_change_negative(self):
        inp = KpiCardInput(label="X", value="100", change_pct=-0.75)
        result = build_kpi_card(inp)
        change_text = result[2].text
        assert "▼" in change_text
        assert "-0,75%" in change_text

    def test_change_none_empty(self):
        inp = KpiCardInput(label="X", value="100", change_pct=None)
        result = build_kpi_card(inp)
        assert result[2].text == ""

    # ---- v0.4.3 (S241 KT-1 B-7): Pfeil-Glyph konsistent in allen 3 Stufen ----
    # Vorher (v0.4.1+) trug die unter-Threshold-Stufe einen Bullet-Punkt "•",
    # der visuell deutlich kleiner als die ▲/▼ wirkte (KT-1 Briefing-Befund S241).
    # Jetzt: alle drei Stufen tragen ▲ oder ▼ in derselben Groesse, nur die
    # Farbe variiert (muted-grau bei <0.5%, success-gruen / error-rot ab 0.5%).

    def test_change_below_threshold_positive_is_muted_arrow(self):
        """|Δ|<0.5% positiv → muted (grau), aber ▲ in voller Groesse (kein Bullet)."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.30)
        text = build_kpi_card(inp)[2].text
        assert "▲" in text
        assert "•" not in text
        assert "+0,30%" in text
        # color.viz.muted = #b0bec5
        assert "b0bec5" in text.lower()

    def test_change_below_threshold_negative_is_muted_arrow(self):
        """|Δ|<0.5% negativ → muted (grau), ▼ in voller Groesse (kein Bullet)."""
        inp = KpiCardInput(label="X", value="100", change_pct=-0.20)
        text = build_kpi_card(inp)[2].text
        assert "▼" in text
        assert "•" not in text
        assert "-0,20%" in text
        assert "b0bec5" in text.lower()

    def test_change_zero_is_muted_arrow(self):
        """change_pct=0.0 → muted, ▲ (Default Up bei Sign==0), +0,00%."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.0)
        text = build_kpi_card(inp)[2].text
        assert "▲" in text or "▼" in text
        assert "•" not in text
        assert "+0,00%" in text

    def test_change_at_threshold_positive_is_strong(self):
        """change_pct=0.5 (genau Schwelle) → kraeftig, Pfeil, success-color."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.5)
        text = build_kpi_card(inp)[2].text
        assert "▲" in text
        assert "+0,50%" in text
        # color.status.success = #2e7d32
        assert "2e7d32" in text.lower()

    def test_change_at_threshold_negative_is_strong(self):
        inp = KpiCardInput(label="X", value="100", change_pct=-0.5)
        text = build_kpi_card(inp)[2].text
        assert "▼" in text
        assert "-0,50%" in text
        assert "d32f2f" in text.lower()

    def test_change_just_below_threshold_is_muted_arrow(self):
        """0.499% (knapp unter 0.5%) → muted, aber ▲ statt Bullet."""
        inp = KpiCardInput(label="X", value="100", change_pct=0.499)
        text = build_kpi_card(inp)[2].text
        assert "▲" in text
        assert "•" not in text
        assert "b0bec5" in text.lower()

    def test_sparkline_with_values(self):
        inp = KpiCardInput(
            label="X", value="100", sparkline_values=[1.0, 2.0, 3.0, 4.0]
        )
        result = build_kpi_card(inp)
        # Sparkline-Slot ist ein ReportLab Drawing
        assert isinstance(result[3], Drawing)

    def test_sparkline_without_values_is_spacer(self):
        inp = KpiCardInput(label="X", value="100", sparkline_values=None)
        result = build_kpi_card(inp)
        assert isinstance(result[3], Spacer)

    def test_sparkline_with_one_value_is_spacer(self):
        """Mit nur 1 Wert (zu wenig fuer Sparkline) wird Spacer genutzt."""
        inp = KpiCardInput(label="X", value="100", sparkline_values=[1.0])
        result = build_kpi_card(inp)
        assert isinstance(result[3], Spacer)

    def test_caption_string(self):
        inp = KpiCardInput(label="X", value="100", caption="Stand: 04:50")
        result = build_kpi_card(inp)
        assert isinstance(result[4], Paragraph)
        assert result[4].text == "Stand: 04:50"

    def test_caption_empty_when_none(self):
        inp = KpiCardInput(label="X", value="100", caption=None)
        result = build_kpi_card(inp)
        assert result[4].text == ""


# ---------------------------------------------------------------------------
# v0.16.0: Caption-Schrift kommt aus dem Token, nicht aus einem Literal
# ---------------------------------------------------------------------------


class TestCaptionSchrift:
    def test_caption_nutzt_den_zitat_token(self):
        from mn_design_system.helpers import font_family

        inp = KpiCardInput(label="X", value="100", caption="Stand: 04:50")
        caption = build_kpi_card(inp)[-1]
        assert isinstance(caption, Paragraph)
        assert caption.style.fontName == font_family("italic-editorial")

    def test_fett_in_der_caption_bleibt_fett_kursiv(self):
        """Mit dem Token als Grundschrift gilt die Familie der Zitat-Kursive: <b> geht
        nicht mehr still verloren."""
        inp = KpiCardInput(label="X", value="100", caption="Stand <b>04:50</b>")
        caption = build_kpi_card(inp)[-1]
        namen = {frag.fontName for frag in caption.frags}
        assert "SourceSerif4-BoldItalic" in namen


# ---------------------------------------------------------------------------
# 0.17.1 — Polaritaet und absolutes Delta (derselbe Vertrag wie im Web)
# ---------------------------------------------------------------------------

#: Ausgabe von 0.17.0, woertlich — alte Aufrufe bleiben bytegleich.
_ALT_CHANGE = {
    1.25: '<font color="#2e7d32">▲ +1,25%</font>',
    -2.3: '<font color="#D32F2F">▼ -2,30%</font>',
    0.2: '<font color="#b0bec5">▲ +0,20%</font>',
    -0.2: '<font color="#b0bec5">▼ -0,20%</font>',
    0.0: '<font color="#b0bec5">▲ +0,00%</font>',
    0.5: '<font color="#2e7d32">▲ +0,50%</font>',
    -0.5: '<font color="#D32F2F">▼ -0,50%</font>',
}


class TestAlteAufrufeUnveraendert:
    @pytest.mark.parametrize("pct", sorted(_ALT_CHANGE))
    def test_change_ist_bytegleich(self, pct):
        text = build_kpi_card(KpiCardInput(label="X", value="1", change_pct=pct))[
            2
        ].text
        assert text == _ALT_CHANGE[pct]

    @pytest.mark.parametrize("pct", sorted(_ALT_CHANGE))
    def test_explizites_hoeher_ist_der_alte_aufruf(self, pct):
        karte = KpiCardInput(label="X", value="1", change_pct=pct, richtung="hoeher")
        assert build_kpi_card(karte)[2].text == _ALT_CHANGE[pct]

    def test_ohne_change_bleibt_leer(self):
        assert build_kpi_card(KpiCardInput(label="X", value="1"))[2].text == ""


class TestPolaritaetPdf:
    SUCCESS = "2e7d32"
    ERROR = "d32f2f"
    MUTED = "b0bec5"

    @pytest.mark.parametrize(
        ("richtung", "pct", "farbe"),
        [
            ("niedriger", -2.0, SUCCESS),
            ("niedriger", 2.0, ERROR),
            ("niedriger", 0.2, MUTED),
            ("neutral", 2.0, MUTED),
            ("neutral", -2.0, MUTED),
        ],
    )
    def test_prozent_faerbt_nach_wertung(self, richtung, pct, farbe):
        karte = KpiCardInput(label="X", value="1", change_pct=pct, richtung=richtung)
        text = build_kpi_card(karte)[2].text.lower()
        assert f'color="#{farbe}"' in text
        assert ("▲" if pct >= 0 else "▼") in text  # Pfeil = Bewegung, nicht Wertung

    def test_gewicht_ruecklauf_ist_gruen_mit_echtem_minus(self):
        karte = KpiCardInput(
            label="Gewicht",
            value="72,4 kg",
            delta_wert=-1.2,
            delta_einheit="kg",
            richtung="niedriger",
        )
        text = build_kpi_card(karte)[2].text
        assert text == f'<font color="#2e7d32">▼ {MINUS}1,2{NBSP}kg</font>'

    def test_anstieg_bei_niedriger_ist_rot(self):
        karte = KpiCardInput(
            label="Gewicht",
            value="73,4 kg",
            delta_wert=1.0,
            delta_einheit="kg",
            richtung="niedriger",
        )
        text = build_kpi_card(karte)[2].text
        assert text == f'<font color="#D32F2F">▲ +1,0{NBSP}kg</font>'

    def test_tausenderpunkt_wird_nicht_zum_komma(self):
        """Der alte Prozentpfad ersetzt jeden Punkt durch ein Komma — das Delta
        kommt schon deutsch an und darf dabei nicht kaputtgehen."""
        karte = KpiCardInput(
            label="Schritte", value="9.800", delta_wert=1250.0, dezimalstellen=0
        )
        assert "+1.250" in build_kpi_card(karte)[2].text

    def test_unveraendert_ohne_pfeil_gedaempft(self):
        karte = KpiCardInput(label="X", value="1", delta_wert=-0.04, delta_einheit="kg")
        text = build_kpi_card(karte)[2].text
        assert text == '<font color="#b0bec5">unverändert</font>'

    def test_einheit_wird_fuer_reportlab_escaped(self):
        karte = KpiCardInput(label="X", value="1", delta_wert=1.0, delta_einheit="<b>")
        assert "&lt;b&gt;" in build_kpi_card(karte)[2].text

    def test_paragraph_baut_ohne_fehler(self):
        """Der Paragraph wird gewrappt — ein kaputtes Markup wirft hier."""
        karte = KpiCardInput(
            label="X",
            value="1",
            delta_wert=-1.2,
            delta_einheit="kg",
            richtung="niedriger",
        )
        flowable = build_kpi_card(karte)[2]
        flowable.wrap(200, 100)
