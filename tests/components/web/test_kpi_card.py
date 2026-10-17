"""Tests fuer Web-KPI-Card-Renderer (Welle E.0; Polaritaet und Delta 0.17.1)."""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns._zahl import MINUS, NBSP
from mn_design_system.components._patterns.contracts import KpiCardInput
from mn_design_system.components.web.kpi_card import (
    render_kpi_card_css,
    render_kpi_card_html,
)
from mn_design_system.tokens import get


class TestRenderKpiCardHtml:
    def test_minimal_renders(self):
        html = render_kpi_card_html(KpiCardInput(label="DAX", value="22.450"))
        assert '<article class="mn-kpi-card">' in html
        assert "DAX" in html
        assert "22.450" in html
        assert "</article>" in html

    def test_change_pct_up_class(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", change_pct=1.5)
        )
        assert "is-up" in html
        assert "+1.50%" in html
        assert "▲" in html

    def test_change_pct_down_class(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", change_pct=-2.3)
        )
        assert "is-down" in html
        assert "-2.30%" in html
        assert "▼" in html

    def test_change_pct_neutral_class(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", change_pct=0.0)
        )
        assert "is-neutral" in html

    def test_no_change_pct_omits_change(self):
        html = render_kpi_card_html(KpiCardInput(label="X", value="100"))
        assert "mn-kpi-card__change" not in html

    def test_sparkline_embedded_when_values(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="X",
                value="100",
                sparkline_values=[1.0, 2.0, 3.0, 4.0, 5.0],
            )
        )
        assert "<svg" in html
        assert "mn-kpi-card__sparkline" in html

    def test_caption_when_provided(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100", caption="30 Tage")
        )
        assert "30 Tage" in html
        assert "mn-kpi-card__caption" in html

    def test_xss_label_escaped(self):
        html = render_kpi_card_html(
            KpiCardInput(label="<script>alert(1)</script>", value="100")
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_value_escaped(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="<img src=x onerror=alert(1)>")
        )
        assert "<img" not in html
        assert "&lt;img" in html

    def test_inline_css_embedded(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="100"), inline_css=True
        )
        assert "<style>" in html
        assert ".mn-kpi-card" in html

    def test_inline_css_off_by_default(self):
        html = render_kpi_card_html(KpiCardInput(label="X", value="100"))
        assert "<style>" not in html


class TestRenderKpiCardCss:
    def test_returns_css_string(self):
        css = render_kpi_card_css()
        assert ".mn-kpi-card {" in css
        assert ".mn-kpi-card__label {" in css
        assert ".mn-kpi-card__value {" in css

    def test_uses_css_custom_properties(self):
        css = render_kpi_card_css()
        assert "var(--color-light-h1" in css
        assert "var(--color-status-success" in css
        assert "var(--color-status-error" in css

    def test_css_has_layout_only_no_token_values(self):
        # Token-Werte sollen ausschliesslich ueber var(--...) kommen.
        # Konkrete Hex-Werte (Fallbacks fuer Konsumenten ohne tokens.css) sind erlaubt.
        css = render_kpi_card_css()
        # Layout-Eigenschaften muessen vorhanden sein
        assert "padding" in css
        assert "border-radius" in css
        assert "font-size" in css

    def test_uses_foundation_tokens(self):
        """Re-Tokenisierung: die KPI-Mikro-Skala (frueher 7-11px) tritt auf die
        Web-Foundation — Label/Change/Caption auf web.text.caption (12px),
        der Headline-Wert auf web.text.h3 (23px)."""
        css = render_kpi_card_css()
        assert "var(--web-text-caption" in css
        assert "var(--web-text-h3" in css
        assert "var(--web-leading-h3" in css
        assert "var(--web-font-sans" in css
        assert "var(--web-stroke-line" in css
        assert "var(--web-color-separator" in css
        assert "var(--space-" in css

    def test_radius_card_fallback_is_4px(self):
        """Der radius-card-Fallback entspricht dem echten Token (4px)."""
        css = render_kpi_card_css()
        assert "var(--radius-card, 4px)" in css

    def test_no_print_pt_units(self):
        """Keine pt-Einheiten — die KPI-Card ist rein web. Die alten
        rem-Kommentare (~9pt/~7pt) sind mit der Re-Tokenisierung weg.

        Geprueft wird auf pt als Einheit ('pt;' / 'pt '), nicht auf das
        Substring 'pt' — der Token-Schritt 'caption' enthaelt es legitim."""
        css = render_kpi_card_css()
        assert "pt;" not in css and "pt " not in css


# ---------------------------------------------------------------------------
# 0.17.1 — alte Aufrufe bleiben bytegleich
# ---------------------------------------------------------------------------


#: Ausgabe von 0.17.0 (vor der Polaritaet), woertlich: wer die Karte schon benutzt,
#: bekommt dasselbe HTML — nicht „ungefaehr dasselbe".
def _artikel(*teile: str) -> str:
    return '<article class="mn-kpi-card">' + "".join(teile) + "</article>"


_ALT = {
    "minimal": (
        {"label": "DAX", "value": "22.450"},
        _artikel(
            '<div class="mn-kpi-card__label">DAX</div>',
            '<div class="mn-kpi-card__value">22.450</div>',
        ),
    ),
    "hoch": (
        {
            "label": "DAX",
            "value": "22.450",
            "change_pct": 1.25,
            "caption": "Stand: Vortag",
        },
        _artikel(
            '<div class="mn-kpi-card__label">DAX</div>',
            '<div class="mn-kpi-card__value">22.450</div>',
            '<div class="mn-kpi-card__change is-up">▲ +1.25%</div>',
            '<div class="mn-kpi-card__caption">Stand: Vortag</div>',
        ),
    ),
    "runter": (
        {"label": "X", "value": "100", "change_pct": -2.3},
        _artikel(
            '<div class="mn-kpi-card__label">X</div>',
            '<div class="mn-kpi-card__value">100</div>',
            '<div class="mn-kpi-card__change is-down">▼ -2.30%</div>',
        ),
    ),
    "neutral": (
        {"label": "X", "value": "100", "change_pct": 0.2},
        _artikel(
            '<div class="mn-kpi-card__label">X</div>',
            '<div class="mn-kpi-card__value">100</div>',
            '<div class="mn-kpi-card__change is-neutral">■ +0.20%</div>',
        ),
    ),
    "sparkline": (
        {
            "label": "X",
            "value": "100",
            "change_pct": 0.0,
            "sparkline_values": [1.0, 2.0, 3.0],
            "caption": "30 Tage",
        },
        _artikel(
            '<div class="mn-kpi-card__label">X</div>',
            '<div class="mn-kpi-card__value">100</div>',
            '<div class="mn-kpi-card__change is-neutral">■ 0.00%</div>',
            '<div class="mn-kpi-card__sparkline">',
            '<svg xmlns="http://www.w3.org/2000/svg" width="120.00" height="24.00" ',
            'viewBox="0 0 120.00 24.00" class="mn-sparkline" aria-hidden="true">',
            '<path d="M 0.00 24.00 L 60.00 12.00 L 120.00 0.00" fill="none" ',
            'stroke="#4338ca" stroke-width="1.2" stroke-linejoin="round" ',
            'stroke-linecap="round"/></svg></div>',
            '<div class="mn-kpi-card__caption">30 Tage</div>',
        ),
    ),
}


class TestAlteAufrufeUnveraendert:
    @pytest.mark.parametrize("name", sorted(_ALT))
    def test_html_ist_bytegleich(self, name):
        eingabe, soll = _ALT[name]
        assert render_kpi_card_html(KpiCardInput(**eingabe)) == soll

    @pytest.mark.parametrize("name", sorted(_ALT))
    def test_explizites_hoeher_ist_der_alte_aufruf(self, name):
        eingabe, soll = _ALT[name]
        assert render_kpi_card_html(KpiCardInput(**eingabe, richtung="hoeher")) == soll

    def test_alte_css_regeln_stehen_unveraendert_vor_den_neuen(self):
        """Die Regeln von 0.17.0 bleiben als Block erhalten; die neuen kommen NACH
        ihnen (gleiche Spezifitaet: die spaetere gewinnt)."""
        css = render_kpi_card_css()
        alt = (
            ".mn-kpi-card__change.is-neutral {\n"
            "  color: var(--color-light-text-muted, #6b7280);\n}\n"
        )
        assert alt in css
        assert css.index(".is-up {") < css.index(".is-gut {")
        assert css.index(".is-down {") < css.index(".is-schlecht {")
        assert css.index(".is-neutral {") < css.index(".is-ungewertet {")


# ---------------------------------------------------------------------------
# 0.17.1 — Polaritaet
# ---------------------------------------------------------------------------


def _aenderung(html: str) -> str:
    """Die Zeile der Veraenderung (``<div class="mn-kpi-card__change …">…</div>``)."""
    anfang = html.index('<div class="mn-kpi-card__change')
    return html[anfang : html.index("</div>", anfang) + len("</div>")]


class TestPolaritaetProzent:
    @pytest.mark.parametrize(
        ("richtung", "pct", "soll"),
        [
            (
                "niedriger",
                -2.3,
                '<div class="mn-kpi-card__change is-down is-gut">▼ -2.30%</div>',
            ),
            (
                "niedriger",
                2.3,
                '<div class="mn-kpi-card__change is-up is-schlecht">▲ +2.30%</div>',
            ),
            (
                "niedriger",
                0.2,
                '<div class="mn-kpi-card__change is-neutral">■ +0.20%</div>',
            ),
            (
                "neutral",
                2.3,
                '<div class="mn-kpi-card__change is-up is-ungewertet">▲ +2.30%</div>',
            ),
            (
                "neutral",
                -2.3,
                '<div class="mn-kpi-card__change is-down is-ungewertet">▼ -2.30%</div>',
            ),
            (
                "neutral",
                0.2,
                '<div class="mn-kpi-card__change is-neutral">■ +0.20%</div>',
            ),
        ],
    )
    def test_klassen_nach_bewegung_und_wertung(self, richtung, pct, soll):
        karte = KpiCardInput(label="X", value="1", change_pct=pct, richtung=richtung)
        assert _aenderung(render_kpi_card_html(karte)) == soll


class TestAbsolutesDelta:
    def test_gewicht_ruecklauf_ist_gut(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="Gewicht",
                value="72,4 kg",
                delta_wert=-1.2,
                delta_einheit="kg",
                richtung="niedriger",
            )
        )
        assert _aenderung(html) == (
            f'<div class="mn-kpi-card__change is-down is-gut">▼ {MINUS}1,2{NBSP}kg</div>'
        )

    def test_gewicht_anstieg_ist_schlecht(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="Gewicht",
                value="73,4 kg",
                delta_wert=1.0,
                delta_einheit="kg",
                richtung="niedriger",
            )
        )
        assert _aenderung(html) == (
            f'<div class="mn-kpi-card__change is-up is-schlecht">▲ +1,0{NBSP}kg</div>'
        )

    def test_schritte_anstieg_ist_gut_mit_tausenderpunkt(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="Schritte",
                value="9.800",
                delta_wert=1250.0,
                delta_einheit="Schritte",
                dezimalstellen=0,
            )
        )
        assert _aenderung(html) == (
            f'<div class="mn-kpi-card__change is-up">▲ +1.250{NBSP}Schritte</div>'
        )

    def test_auf_null_gerundet_ist_unveraendert_und_neutral(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="Gewicht",
                value="72,4 kg",
                delta_wert=-0.04,
                delta_einheit="kg",
                richtung="niedriger",
            )
        )
        assert _aenderung(html) == (
            '<div class="mn-kpi-card__change is-neutral">■ unverändert</div>'
        )

    def test_neutrale_richtung_zeigt_die_bewegung_ohne_wertung(self):
        html = render_kpi_card_html(
            KpiCardInput(
                label="Schlaf",
                value="7 h",
                delta_wert=-0.5,
                delta_einheit="h",
                richtung="neutral",
            )
        )
        assert 'class="mn-kpi-card__change is-down is-ungewertet"' in html
        assert f"▼ {MINUS}0,5{NBSP}h" in html

    def test_einheit_wird_escaped(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="1", delta_wert=1.0, delta_einheit="<b>&</b>")
        )
        assert "<b>" not in html
        assert "&lt;b&gt;&amp;&lt;/b&gt;" in html

    def test_ohne_delta_keine_zeile(self):
        html = render_kpi_card_html(
            KpiCardInput(label="X", value="1", richtung="niedriger")
        )
        assert "mn-kpi-card__change" not in html


class TestCssWertungsklassen:
    def test_regeln_mit_den_status_tokens(self):
        css = render_kpi_card_css()
        assert (
            ".mn-kpi-card__change.is-gut {\n"
            "  color: var(--color-status-success, #2e7d32);\n}"
        ) in css
        assert (
            ".mn-kpi-card__change.is-schlecht {\n"
            "  color: var(--color-status-error, #d32f2f);\n}"
        ) in css
        assert (
            ".mn-kpi-card__change.is-ungewertet {\n"
            "  color: var(--color-light-text-muted, #6b7280);\n}"
        ) in css

    def test_fallbacks_sind_die_echten_token_werte(self):
        css = render_kpi_card_css().lower()
        assert f"var(--color-status-success, {get('color.status.success')})" in css
        assert f"var(--color-status-error, {get('color.status.error').lower()})" in css
        assert f"var(--color-light-text-muted, {get('color.light.text-muted')})" in css
