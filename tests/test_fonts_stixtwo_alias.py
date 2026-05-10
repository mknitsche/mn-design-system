"""Test fuer STIXTwoText-Alias-Registrierung (v0.5.1 / macb-S249).

Hintergrund: helpers.font_with_fallback wrappt Greek-Letters in
<font name="STIXTwoText">...</font>-Tags, aber fonts/__init__.py registrierte
zuvor nur "STIXTwo" (kurz). Ergebnis: ReportLab ValueError beim Rendern, weil
"STIXTwoText" nicht in pdfmetrics aufgeloest werden konnte. Daily-Engine
2026-05-10 Phase 4-render schlug genau so fehl (claudeAI macb-S249 Bug-Trail).

Fix: Alias-Eintraege fuer STIXTwoText* in _FONT_MAP, sodass beide Namen
registriert sind. Der Test sichert das Verhalten gegen Drift.
"""

from __future__ import annotations

from io import BytesIO

import pytest
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate

from mn_design_system.fonts import register_all_fonts


@pytest.fixture(autouse=True)
def _register_fonts():
    """Registriert alle Default-Fonts (idempotent)."""
    register_all_fonts()


class TestStixTwoTextAlias:
    def test_stixtwo_short_name_registered(self):
        """Der kurze Name STIXTwo ist registriert (Bestandsschutz).

        BoldItalic-Variante absichtlich nicht geprueft: das Asset
        STIXTwoText-BoldItalic.ttf liegt nicht im stix-two/-Verzeichnis.
        """
        names = pdfmetrics.getRegisteredFontNames()
        assert "STIXTwo" in names
        assert "STIXTwo-Italic" in names
        assert "STIXTwo-Bold" in names

    def test_stixtwotext_alias_registered(self):
        """Der lange Name STIXTwoText ist als Alias registriert.

        Nach Bug-Fix S249 muessen beide Namen verfuegbar sein, weil
        helpers.font_with_fallback Tags mit STIXTwoText schreibt.
        """
        names = pdfmetrics.getRegisteredFontNames()
        assert "STIXTwoText" in names, (
            "STIXTwoText muss als Alias registriert sein, "
            "weil helpers.font_with_fallback diesen Namen in <font>-Tags "
            "schreibt. Sonst ValueError im PDF-Rendering."
        )
        assert "STIXTwoText-Italic" in names
        assert "STIXTwoText-Bold" in names

    def test_render_paragraph_with_stixtwotext_tag(self):
        """ReportLab-Render-Smoke: <font name="STIXTwoText"> muss aufloesbar sein."""
        styles = getSampleStyleSheet()
        # Genau das Markup das helpers.font_with_fallback erzeugt
        markup = (
            'Vol-Spike <font name="STIXTwoText">σ</font> ueber Median, '
            '<font name="STIXTwoText">α/β/γ</font> Vergleich.'
        )
        para = Paragraph(markup, styles["BodyText"])
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        # Wuerde vor dem Fix mit ValueError("Can't map ... stixtwotext") werfen
        doc.build([para])
        assert buf.getvalue().startswith(b"%PDF"), "PDF-Output erwartet"
