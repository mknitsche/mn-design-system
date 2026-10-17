"""Tests fuer die Web-Zeitraum-Leiste (0.17.1).

Segment-Leiste aus Links fuer ``?tage=30|90|365``: ein <nav>, je Option ein <a>, der
aktive Zustand traegt ``aria-current="page"``. Reines HTML + CSS, kein Skript.
"""

from __future__ import annotations

import re

import pytest

from mn_design_system.components._patterns.contracts import (
    ZeitraumLeisteInput,
    ZeitraumOption,
)
from mn_design_system.components.web import (
    render_zeitraum_leiste_css,
    render_zeitraum_leiste_html,
)
from mn_design_system.tokens import get


def _eingabe(aktiv: int | None = 1, **kw) -> ZeitraumLeisteInput:
    namen = [("30 Tage", "?tage=30"), ("90 Tage", "?tage=90"), ("1 Jahr", "?tage=365")]
    return ZeitraumLeisteInput(
        optionen=[
            ZeitraumOption(label=label, href=href, active=i == aktiv)
            for i, (label, href) in enumerate(namen)
        ],
        **kw,
    )


class TestHtml:
    def test_aufbau(self):
        html = render_zeitraum_leiste_html(_eingabe(aktiv=0))
        assert html == (
            '<nav class="mn-zeitraum-leiste" aria-label="Zeitraum">'
            '<a class="mn-zeitraum-leiste__option" href="?tage=30" '
            'aria-current="page">30 Tage</a>'
            '<a class="mn-zeitraum-leiste__option" href="?tage=90">90 Tage</a>'
            '<a class="mn-zeitraum-leiste__option" href="?tage=365">1 Jahr</a>'
            "</nav>"
        )

    @pytest.mark.parametrize("aktiv", [0, 1, 2])
    def test_genau_die_aktive_option_traegt_aria_current(self, aktiv):
        html = render_zeitraum_leiste_html(_eingabe(aktiv=aktiv))
        assert html.count("aria-current") == 1
        links = re.findall(r"<a [^>]*>[^<]*</a>", html)
        assert len(links) == 3
        for i, link in enumerate(links):
            assert ('aria-current="page"' in link) == (i == aktiv), link

    def test_ohne_aktive_option_kein_aria_current(self):
        html = render_zeitraum_leiste_html(_eingabe(aktiv=None))
        assert "aria-current" not in html

    def test_jede_option_ist_ein_link(self):
        """Links, keine Schaltflaechen: ``?tage=`` ist eine Adresse (Zurueck-Knopf,
        Lesezeichen, kein Skript noetig)."""
        html = render_zeitraum_leiste_html(_eingabe())
        assert "<button" not in html
        assert (
            len(re.findall(r'<a class="mn-zeitraum-leiste__option" href="', html)) == 3
        )

    def test_aria_label_ist_einstellbar(self):
        html = render_zeitraum_leiste_html(_eingabe(aria_label="Zeitraum Gewicht"))
        assert 'aria-label="Zeitraum Gewicht"' in html

    def test_label_href_und_aria_label_werden_escaped(self):
        inp = ZeitraumLeisteInput(
            optionen=[
                ZeitraumOption(label="<b>30</b>", href='?a="1"&b=2', active=True),
                ZeitraumOption(label="90", href="?tage=90"),
            ],
            aria_label='Zeit "raum" <x>',
        )
        html = render_zeitraum_leiste_html(inp)
        assert "<b>" not in html
        assert "&lt;b&gt;30&lt;/b&gt;" in html
        assert 'href="?a=&quot;1&quot;&amp;b=2"' in html
        assert 'aria-label="Zeit &quot;raum&quot; &lt;x&gt;"' in html

    def test_nichts_inline_fuer_eine_strenge_csp(self):
        """Kein ``style=``, kein ``<script>``, kein ``on…=``-Attribut: die Seitenhuelle
        des Konsumenten erlaubt ``style-src 'self'`` und ``script-src 'self'``."""
        html = render_zeitraum_leiste_html(_eingabe())
        assert "style=" not in html
        assert "<script" not in html
        assert not re.search(r"\son[a-z]+=", html)

    def test_inline_css_haengt_den_style_block_vorn_an(self):
        html = render_zeitraum_leiste_html(_eingabe(), inline_css=True)
        assert html.startswith("<style>")
        assert ".mn-zeitraum-leiste" in html.split("</style>")[0]

    def test_inline_css_ist_standardmaessig_aus(self):
        assert "<style>" not in render_zeitraum_leiste_html(_eingabe())


class TestCss:
    def test_touch_ziel_nach_token_in_beide_richtungen(self):
        """Mindestens 44 x 44 px: hoch UND breit (ein kurzes Label wie „1 J" bliebe
        sonst schmaler als ein Finger)."""
        css = render_zeitraum_leiste_css()
        touch = get("web.touch-target")
        assert touch == "44px"
        assert f"min-height: var(--web-touch-target, {touch});" in css
        assert f"min-width: var(--web-touch-target, {touch});" in css

    def test_aktiver_zustand_haengt_am_attribut(self):
        css = render_zeitraum_leiste_css()
        assert '.mn-zeitraum-leiste__option[aria-current="page"] {' in css
        # Eine Wahrheit: es gibt keine zweite Klasse, die „aktiv" nur aussehen laesst.
        assert "is-active" not in css

    def test_aktiv_steht_nach_hover(self):
        """Gleiche Spezifitaet: die spaetere Regel gewinnt — die aktive Option bleibt
        beim Ueberfahren aktiv."""
        css = render_zeitraum_leiste_css()
        assert css.index(":hover {") < css.index('[aria-current="page"] {')

    def test_fokusring_aus_den_tokens(self):
        css = render_zeitraum_leiste_css()
        assert ".mn-zeitraum-leiste__option:focus-visible {" in css
        assert "var(--web-stroke-focus, 2px)" in css
        assert f"var(--web-color-focus-ring, {get('web.color.focus-ring')})" in css

    def test_fallbacks_sind_die_echten_token_werte(self):
        """Greift ein Fallback (tokens.css fehlt), sieht die Leiste trotzdem richtig
        aus — der Wert ist der des Tokens, kein Raten."""
        css = render_zeitraum_leiste_css().lower()
        for var, token in [
            ("--color-light-surface", "color.light.surface"),
            ("--web-color-separator", "web.color.separator"),
            ("--color-light-text-muted", "color.light.text-muted"),
            ("--color-light-text", "color.light.text"),
            ("--color-light-surface-subtle", "color.light.surface-subtle"),
            ("--color-indigo-50", "color.indigo.50"),
            ("--color-light-accent", "color.light.accent"),
            ("--web-stroke-line", "web.stroke.line"),
            ("--web-text-ui", "web.text.ui"),
        ]:
            assert f"var({var}, {get(token).lower()})" in css, var

    def test_keine_festen_masse_ausser_den_token_fallbacks(self):
        """Hoehe, Breite, Abstand und Schriftgroesse kommen aus Tokens."""
        css = render_zeitraum_leiste_css()
        for zeile in css.splitlines():
            if re.search(r"(min-height|min-width|font-size|padding)\s*:", zeile):
                assert "var(" in zeile, zeile

    def test_keine_pt_einheiten(self):
        css = render_zeitraum_leiste_css()
        assert "pt;" not in css and "pt " not in css


def _luminanz(hexfarbe: str) -> float:
    r, g, b = (int(hexfarbe[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _kontrast(a: str, b: str) -> float:
    hell, dunkel = sorted((_luminanz(a), _luminanz(b)), reverse=True)
    return (hell + 0.05) / (dunkel + 0.05)


class TestKontrast:
    """WCAG 1.4.3: Text >= 4,5:1 in jedem der drei Zustaende."""

    def test_ruhend(self):
        assert (
            _kontrast(get("color.light.text-muted"), get("color.light.surface")) >= 4.5
        )

    def test_hover(self):
        assert (
            _kontrast(get("color.light.text"), get("color.light.surface-subtle")) >= 4.5
        )

    def test_aktiv(self):
        assert _kontrast(get("color.light.accent"), get("color.indigo.50")) >= 4.5
