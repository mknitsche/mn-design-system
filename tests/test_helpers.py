"""Tests fuer mn_design_system.helpers (v0.4.4 / S248).

Strict-Mode: KeyError bei unbekanntem Token.
Konvertierung: 1 unit = 1mm = 2.835pt = 4px.
"""

from __future__ import annotations

import pytest

from mn_design_system import (
    MM_TO_PT,
    color_token,
    font_family,
    font_with_fallback,
    leading_token,
    size_token,
    space_token,
)


# ----------------------------------------------------------------------------
# space_token
# ----------------------------------------------------------------------------


class TestSpaceToken:
    def test_mm_default_unit(self):
        assert space_token("space.4") == 4.0

    def test_pt_conversion(self):
        # 4mm = 11.3386pt
        assert space_token("space.4", unit="pt") == pytest.approx(11.3386, abs=0.001)

    def test_px_conversion(self):
        # Konvention: 1mm = 4px
        assert space_token("space.4", unit="px") == 16.0

    def test_raw_unit_returns_mm_value(self):
        assert space_token("space.4", unit="raw") == 4.0

    def test_semantic_alias(self):
        # space.semantic.default -> 12px = 3mm
        assert space_token("space.semantic.default") == 3.0
        assert space_token("space.semantic.tight-min") == 1.0
        assert space_token("space.semantic.section") == 12.0

    def test_indent_token(self):
        assert space_token("space.indent.bullet") == 3.0
        assert space_token("space.indent.subitem") == 6.0

    def test_page_margin_in_mm(self):
        # space.page.margin-top ist "22mm" - direkt mm-formatiert
        assert space_token("space.page.margin-top") == 22.0

    def test_strict_mode_unknown_key(self):
        with pytest.raises(KeyError, match="Unknown spacing token"):
            space_token("space.does-not-exist")

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            space_token("space.4", unit="weird")


# ----------------------------------------------------------------------------
# size_token
# ----------------------------------------------------------------------------


class TestSizeToken:
    def test_short_key(self):
        assert size_token("body") == 9.5

    def test_full_key(self):
        assert size_token("font.size.body") == 9.5

    def test_new_v044_tokens(self):
        # S248 KT-1: Footer-Familie + Title-Page
        assert size_token("footer-page") == 8.0
        assert size_token("disclaimer") == 8.0
        assert size_token("source") == 8.0
        assert size_token("title-page") == 22.0
        assert size_token("icon-large") == 22.0

    def test_pt_default(self):
        assert size_token("h2") == 15.0

    def test_mm_conversion(self):
        # 9.5pt -> ~3.351mm
        assert size_token("body", unit="mm") == pytest.approx(3.351, abs=0.01)

    def test_px_conversion(self):
        # 9.5pt -> ~12.67px (96 DPI)
        assert size_token("body", unit="px") == pytest.approx(12.67, abs=0.01)

    def test_strict_mode(self):
        with pytest.raises(KeyError, match="Unknown size token"):
            size_token("nonexistent-size")


# ----------------------------------------------------------------------------
# leading_token
# ----------------------------------------------------------------------------


class TestLeadingToken:
    def test_body_leading(self):
        # S242: leading body = 13.5pt
        assert leading_token("body") == 13.5

    def test_new_v044_leadings(self):
        assert leading_token("footer-page") == 10.0
        assert leading_token("title-page") == 26.0

    def test_strict_mode(self):
        with pytest.raises(KeyError):
            leading_token("nonexistent")


# ----------------------------------------------------------------------------
# color_token
# ----------------------------------------------------------------------------


class TestColorToken:
    def test_severity_high(self):
        # S248 Variante F: red-600
        assert color_token("color.severity.high") == "#dc2626"

    def test_severity_medium(self):
        # S248 Variante F: amber-800
        assert color_token("color.severity.medium") == "#a16207"

    def test_severity_low(self):
        # alias auf grey-500
        assert color_token("color.severity.low") == "#6b7280"

    def test_existing_color(self):
        assert color_token("color.indigo.900") == "#312e81"

    def test_strict_mode(self):
        with pytest.raises(KeyError, match="Unknown color token"):
            color_token("color.nonexistent")


# ----------------------------------------------------------------------------
# font_family
# ----------------------------------------------------------------------------


class TestFontFamily:
    def test_sans_default(self):
        assert font_family("sans") == "Geist"

    def test_fallback_greek(self):
        # S248: neuer Token
        assert font_family("fallback-greek") == "STIXTwoText-Greek"

    def test_table_default(self):
        assert font_family("table-default") == "Geist"

    def test_table_data(self):
        assert font_family("table-data") == "JetBrainsMono"

    def test_full_key_works(self):
        assert font_family("font.family.sans") == "Geist"

    def test_strict_mode(self):
        with pytest.raises(KeyError):
            font_family("nonexistent")


# ----------------------------------------------------------------------------
# font_with_fallback (Greek-Letter-Wrapping)
# ----------------------------------------------------------------------------


class TestFontWithFallback:
    def test_no_greek_returns_unchanged(self):
        text = "Hello world, no greek here"
        assert font_with_fallback(text) == text

    def test_single_sigma(self):
        # Sigma-Glyph-Bug aus Briefing
        result = font_with_fallback("Vol-Spike +1,8 σ über Median")
        assert "<font name=\"STIXTwoText-Greek\">σ</font>" in result
        assert "Vol-Spike +1,8 " in result
        assert "über Median" in result

    def test_consecutive_greek_letters(self):
        # alpha/beta/gamma als zusammenhaengender Block
        result = font_with_fallback("α/β/γ Vergleich")
        # Ganzer Block α/β/γ inkl. Slashes wird zusammengewrapped
        assert "<font name=\"STIXTwoText-Greek\">" in result
        assert "Vergleich" in result

    def test_math_operators(self):
        # ∑ (U+2211) ist Math Operator
        result = font_with_fallback("Summe ∑ über alle")
        assert "<font name=\"STIXTwoText-Greek\">∑</font>" in result

    def test_empty_string(self):
        assert font_with_fallback("") == ""

    def test_only_ascii_no_change(self):
        text = "Pure ASCII text 12345 !@#$%"
        assert font_with_fallback(text) == text


# ----------------------------------------------------------------------------
# Integration: gleiche Werte in verschiedenen Einheiten round-trippen
# ----------------------------------------------------------------------------


class TestRoundTrip:
    def test_mm_to_pt_to_mm(self):
        mm_val = space_token("space.4", unit="mm")
        pt_val = mm_val * MM_TO_PT
        back_mm = pt_val / MM_TO_PT
        assert back_mm == pytest.approx(mm_val, abs=0.0001)

    def test_consistent_4mm_across_units(self):
        # Token "space.4" muss konsistent in allen Einheiten sein
        assert space_token("space.4", unit="mm") == 4.0
        assert space_token("space.4", unit="px") == 16.0
        # 4mm = 4 * 2.835 = 11.34pt
        pt = space_token("space.4", unit="pt")
        assert pt == pytest.approx(11.34, abs=0.01)
