"""TDD-Tests fuer Wetter-Strip PDF-Implementierung (Welle B v0.2.0)."""

from __future__ import annotations

import pytest
from mn_design_system.components._patterns.contracts import (
    WetterCategory,
    WetterDay,
    WetterStripInput,
)
from mn_design_system.components.pdf.wetter_strip import build_wetter_strip
from pydantic import ValidationError
from reportlab.platypus import Paragraph, Table

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _day(header="Mi", cat=WetterCategory.SONNIG, tmin=10, tmax=20, precip=20):
    return WetterDay(
        header_label=header,
        category=cat,
        temp_min_c=tmin,
        temp_max_c=tmax,
        precip_pct=precip,
    )


# ---------------------------------------------------------------------------
# Contract-Validation
# ---------------------------------------------------------------------------


class TestWetterStripContract:
    def test_min_3_days(self):
        with pytest.raises(ValidationError):
            WetterStripInput(days=[_day(), _day()], location="Nuernberg")

    def test_max_5_days(self):
        with pytest.raises(ValidationError):
            WetterStripInput(days=[_day()] * 6, location="Nuernberg")

    def test_4_days_valid(self):
        inp = WetterStripInput(days=[_day()] * 4, location="Nuernberg")
        assert len(inp.days) == 4

    def test_header_label_max_length(self):
        with pytest.raises(ValidationError):
            WetterDay(
                header_label="A" * 16,  # > 15
                category=WetterCategory.SONNIG,
                temp_min_c=10,
                temp_max_c=20,
                precip_pct=20,
            )

    def test_precip_range(self):
        with pytest.raises(ValidationError):
            WetterDay(
                header_label="Mi",
                category=WetterCategory.SONNIG,
                temp_min_c=10,
                temp_max_c=20,
                precip_pct=101,  # > 100
            )


# ---------------------------------------------------------------------------
# Build-Output
# ---------------------------------------------------------------------------


class TestBuildWetterStrip:
    def test_returns_flowables_list(self):
        inp = WetterStripInput(days=[_day()] * 3, location="Nuernberg")
        result = build_wetter_strip(inp)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_contains_table(self):
        inp = WetterStripInput(days=[_day()] * 3, location="Nuernberg")
        result = build_wetter_strip(inp)
        tables = [f for f in result if isinstance(f, Table)]
        assert len(tables) == 1

    def test_no_summary_when_none(self):
        inp = WetterStripInput(days=[_day()] * 3, location="Nuernberg", summary_text=None)
        result = build_wetter_strip(inp)
        # Nur Table, kein Summary-Paragraph
        paragraphs = [f for f in result if isinstance(f, Paragraph)]
        assert len(paragraphs) == 0

    def test_with_summary_adds_paragraph(self):
        inp = WetterStripInput(
            days=[_day()] * 3,
            location="Nuernberg",
            summary_text="Klassische Aprilwetter-Mischung.",
        )
        result = build_wetter_strip(inp)
        paragraphs = [f for f in result if isinstance(f, Paragraph)]
        assert len(paragraphs) == 1
        assert "Aprilwetter" in paragraphs[0].text

    def test_summary_xml_escaped(self):
        inp = WetterStripInput(
            days=[_day()] * 3,
            location="Nuernberg",
            summary_text="Wind & Regen <heute>",
        )
        result = build_wetter_strip(inp)
        paragraphs = [f for f in result if isinstance(f, Paragraph)]
        text = paragraphs[0].text
        assert "&amp;" in text
        assert "&lt;" in text
        assert "&gt;" in text

    def test_5_days_supported(self):
        inp = WetterStripInput(days=[_day()] * 5, location="Nuernberg")
        result = build_wetter_strip(inp)
        assert len([f for f in result if isinstance(f, Table)]) == 1

    def test_all_categories_render(self):
        """Alle Wetter-Kategorien sollten ohne Crash gerendert werden."""
        days = [
            _day(cat=cat)
            for cat in list(WetterCategory)[:5]  # 5 Tage = 5 Kategorien
        ]
        inp = WetterStripInput(days=days, location="Nuernberg")
        result = build_wetter_strip(inp)
        assert len(result) >= 1
