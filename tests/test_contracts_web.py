"""Verhaltens-Tests fuer die 13 Web-Tier-Contracts (UX-Welle v0.2).

Die Pydantic-Contracts in components/_patterns/contracts.py sind die API des
Design-Systems — Renderer (web/, pdf/, latex/) muessen sie als Eingabe
akzeptieren. Coverage-100% allein taeuscht: deklarative Pydantic-Felder zaehlen
als ausgefuehrt, ohne dass das Validierungs-VERHALTEN geprueft wird.

Geprueft wird pro BaseModel-Contract (Repo-Konvention, vgl. PDF-Contract-Tests
in tests/components/pdf/test_*.py):
- frozen:        Mutation eines Feldes wirft ValidationError.
- extra=forbid:  unbekanntes Konstruktor-Feld wirft ValidationError.
- Field-Constraints (min_length / max_length / ge / le): gueltiger Input
  akzeptiert, ungueltiger wirft ValidationError.

WebTier ist ein str-Enum — geprueft werden die gueltigen Werte und dass ein
ungueltiger Wert abgelehnt wird.
"""

from __future__ import annotations

import pytest
from mn_design_system.components._patterns.contracts import (
    BrandBarChip,
    BrandBarInput,
    CardGridInput,
    ContentCardInput,
    FooterColumn,
    FooterInput,
    FooterLink,
    PageHeaderInput,
    SubNavInput,
    SubNavTab,
    TierChipInput,
    TopNavInput,
    TopNavItem,
    WebTier,
)
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# WebTier (Enum)
# ---------------------------------------------------------------------------


class TestWebTier:
    """str-Enum der vier Web-Tier von mkn-desk.com."""

    def test_valid_values(self):
        assert WebTier.BIBLIOTHEK.value == "bibliothek"
        assert WebTier.ATELIER.value == "atelier"
        assert WebTier.KABINETT.value == "kabinett"
        assert WebTier.START.value == "start"

    def test_member_count(self):
        """Genau vier Tier — keiner zu viel, keiner fehlt."""
        assert len(WebTier) == 4

    def test_construct_from_string(self):
        assert WebTier("atelier") is WebTier.ATELIER

    def test_invalid_value_rejected(self):
        with pytest.raises(ValueError):
            WebTier("public")

    def test_is_str_enum(self):
        """str-Enum: Member ist String-vergleichbar (Token-Lookup color.tier.*)."""
        assert WebTier.KABINETT == "kabinett"


# ---------------------------------------------------------------------------
# TierChipInput
# ---------------------------------------------------------------------------


class TestTierChipInput:
    def test_minimal_valid(self):
        inp = TierChipInput(tier=WebTier.BIBLIOTHEK, label="Wissen")
        assert inp.bordered is True  # Default

    def test_all_fields(self):
        inp = TierChipInput(tier=WebTier.ATELIER, label="Atelier", bordered=False)
        assert inp.bordered is False

    def test_label_min_length(self):
        with pytest.raises(ValidationError):
            TierChipInput(tier=WebTier.START, label="")

    def test_frozen(self):
        inp = TierChipInput(tier=WebTier.START, label="Start")
        with pytest.raises(ValidationError):
            inp.label = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            TierChipInput(tier=WebTier.START, label="Start", foo="bar")


# ---------------------------------------------------------------------------
# BrandBarChip
# ---------------------------------------------------------------------------


class TestBrandBarChip:
    def test_minimal_valid(self):
        inp = BrandBarChip(tier=WebTier.KABINETT, label="Privat")
        assert inp.tier is WebTier.KABINETT

    def test_label_min_length(self):
        with pytest.raises(ValidationError):
            BrandBarChip(tier=WebTier.KABINETT, label="")

    def test_frozen(self):
        inp = BrandBarChip(tier=WebTier.KABINETT, label="Privat")
        with pytest.raises(ValidationError):
            inp.label = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            BrandBarChip(tier=WebTier.KABINETT, label="Privat", foo="bar")


# ---------------------------------------------------------------------------
# BrandBarInput
# ---------------------------------------------------------------------------


class TestBrandBarInput:
    def test_minimal_valid(self):
        inp = BrandBarInput(brand_text="mkn-desk")
        assert inp.chips == []  # default_factory=list

    def test_with_chips(self):
        chips = [
            BrandBarChip(tier=WebTier.BIBLIOTHEK, label="Bibliothek"),
            BrandBarChip(tier=WebTier.START, label="Stufe START"),
        ]
        inp = BrandBarInput(brand_text="mkn-desk", chips=chips)
        assert len(inp.chips) == 2

    def test_brand_text_min_length(self):
        with pytest.raises(ValidationError):
            BrandBarInput(brand_text="")

    def test_chips_max_length(self):
        """chips: max 3 — der vierte Chip wird abgelehnt."""
        chips = [
            BrandBarChip(tier=WebTier.BIBLIOTHEK, label="A"),
            BrandBarChip(tier=WebTier.ATELIER, label="B"),
            BrandBarChip(tier=WebTier.KABINETT, label="C"),
        ]
        BrandBarInput(brand_text="ok", chips=chips)  # genau 3 ist gueltig
        with pytest.raises(ValidationError):
            BrandBarInput(
                brand_text="zu viel",
                chips=[*chips, BrandBarChip(tier=WebTier.START, label="D")],
            )

    def test_frozen(self):
        inp = BrandBarInput(brand_text="mkn-desk")
        with pytest.raises(ValidationError):
            inp.brand_text = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            BrandBarInput(brand_text="mkn-desk", foo="bar")


# ---------------------------------------------------------------------------
# SubNavTab
# ---------------------------------------------------------------------------


class TestSubNavTab:
    def test_minimal_valid(self):
        inp = SubNavTab(label="Fotografie", href="/atelier/fotografie")
        assert inp.active is False  # Default

    def test_all_fields(self):
        inp = SubNavTab(label="Reisen", href="/atelier/reisen", active=True)
        assert inp.active is True

    def test_label_min_length(self):
        with pytest.raises(ValidationError):
            SubNavTab(label="", href="/x")

    def test_href_min_length(self):
        with pytest.raises(ValidationError):
            SubNavTab(label="X", href="")

    def test_frozen(self):
        inp = SubNavTab(label="X", href="/x")
        with pytest.raises(ValidationError):
            inp.href = "/y"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            SubNavTab(label="X", href="/x", foo="bar")


# ---------------------------------------------------------------------------
# SubNavInput
# ---------------------------------------------------------------------------


class TestSubNavInput:
    def test_minimal_valid(self):
        inp = SubNavInput(
            tier=WebTier.BIBLIOTHEK,
            tabs=[SubNavTab(label="Alle", href="/bibliothek")],
        )
        assert inp.aria_label == "Bereichs-Navigation"  # Default

    def test_custom_aria_label(self):
        inp = SubNavInput(
            tier=WebTier.BIBLIOTHEK,
            tabs=[SubNavTab(label="Alle", href="/bibliothek")],
            aria_label="Bibliothek-Bereiche",
        )
        assert inp.aria_label == "Bibliothek-Bereiche"

    def test_tabs_min_length(self):
        """tabs: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            SubNavInput(tier=WebTier.BIBLIOTHEK, tabs=[])

    def test_aria_label_min_length(self):
        with pytest.raises(ValidationError):
            SubNavInput(
                tier=WebTier.BIBLIOTHEK,
                tabs=[SubNavTab(label="Alle", href="/bibliothek")],
                aria_label="",
            )

    def test_frozen(self):
        inp = SubNavInput(
            tier=WebTier.BIBLIOTHEK,
            tabs=[SubNavTab(label="Alle", href="/bibliothek")],
        )
        with pytest.raises(ValidationError):
            inp.aria_label = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            SubNavInput(
                tier=WebTier.BIBLIOTHEK,
                tabs=[SubNavTab(label="Alle", href="/bibliothek")],
                foo="bar",
            )


# ---------------------------------------------------------------------------
# TopNavItem
# ---------------------------------------------------------------------------


class TestTopNavItem:
    def test_minimal_valid(self):
        inp = TopNavItem(label="Bibliothek", href="/bibliothek", tier=WebTier.BIBLIOTHEK)
        assert inp.active is False  # Default

    def test_all_fields(self):
        inp = TopNavItem(
            label="Atelier", href="/atelier", tier=WebTier.ATELIER, active=True
        )
        assert inp.active is True

    def test_label_min_length(self):
        with pytest.raises(ValidationError):
            TopNavItem(label="", href="/x", tier=WebTier.START)

    def test_href_min_length(self):
        with pytest.raises(ValidationError):
            TopNavItem(label="X", href="", tier=WebTier.START)

    def test_frozen(self):
        inp = TopNavItem(label="X", href="/x", tier=WebTier.START)
        with pytest.raises(ValidationError):
            inp.label = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            TopNavItem(label="X", href="/x", tier=WebTier.START, foo="bar")


# ---------------------------------------------------------------------------
# TopNavInput
# ---------------------------------------------------------------------------


class TestTopNavInput:
    def test_minimal_valid(self):
        inp = TopNavInput(
            items=[TopNavItem(label="Start", href="/start", tier=WebTier.START)]
        )
        assert inp.aria_label == "Hauptnavigation"  # Default

    def test_custom_aria_label(self):
        inp = TopNavInput(
            items=[TopNavItem(label="Start", href="/start", tier=WebTier.START)],
            aria_label="Tier-Wechsel",
        )
        assert inp.aria_label == "Tier-Wechsel"

    def test_items_min_length(self):
        """items: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            TopNavInput(items=[])

    def test_aria_label_min_length(self):
        with pytest.raises(ValidationError):
            TopNavInput(
                items=[TopNavItem(label="Start", href="/start", tier=WebTier.START)],
                aria_label="",
            )

    def test_frozen(self):
        inp = TopNavInput(
            items=[TopNavItem(label="Start", href="/start", tier=WebTier.START)]
        )
        with pytest.raises(ValidationError):
            inp.aria_label = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            TopNavInput(
                items=[TopNavItem(label="Start", href="/start", tier=WebTier.START)],
                foo="bar",
            )


# ---------------------------------------------------------------------------
# PageHeaderInput
# ---------------------------------------------------------------------------


class TestPageHeaderInput:
    def test_minimal_valid(self):
        inp = PageHeaderInput(title="Bibliothek")
        assert inp.lead is None  # Default

    def test_all_fields(self):
        inp = PageHeaderInput(title="Bibliothek", lead="Wissen, geordnet.")
        assert inp.lead == "Wissen, geordnet."

    def test_title_min_length(self):
        with pytest.raises(ValidationError):
            PageHeaderInput(title="")

    def test_frozen(self):
        inp = PageHeaderInput(title="Bibliothek")
        with pytest.raises(ValidationError):
            inp.title = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            PageHeaderInput(title="Bibliothek", foo="bar")


# ---------------------------------------------------------------------------
# FooterLink
# ---------------------------------------------------------------------------


class TestFooterLink:
    def test_minimal_valid(self):
        inp = FooterLink(label="Impressum", href="/impressum")
        assert inp.href == "/impressum"

    def test_label_min_length(self):
        with pytest.raises(ValidationError):
            FooterLink(label="", href="/x")

    def test_href_min_length(self):
        with pytest.raises(ValidationError):
            FooterLink(label="X", href="")

    def test_frozen(self):
        inp = FooterLink(label="Impressum", href="/impressum")
        with pytest.raises(ValidationError):
            inp.href = "/datenschutz"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            FooterLink(label="Impressum", href="/impressum", foo="bar")


# ---------------------------------------------------------------------------
# FooterColumn
# ---------------------------------------------------------------------------


class TestFooterColumn:
    def test_minimal_valid(self):
        inp = FooterColumn(
            title="Rechtliches",
            links=[FooterLink(label="Impressum", href="/impressum")],
        )
        assert len(inp.links) == 1

    def test_title_min_length(self):
        with pytest.raises(ValidationError):
            FooterColumn(
                title="", links=[FooterLink(label="Impressum", href="/impressum")]
            )

    def test_links_min_length(self):
        """links: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            FooterColumn(title="Rechtliches", links=[])

    def test_frozen(self):
        inp = FooterColumn(
            title="Rechtliches",
            links=[FooterLink(label="Impressum", href="/impressum")],
        )
        with pytest.raises(ValidationError):
            inp.title = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            FooterColumn(
                title="Rechtliches",
                links=[FooterLink(label="Impressum", href="/impressum")],
                foo="bar",
            )


# ---------------------------------------------------------------------------
# FooterInput
# ---------------------------------------------------------------------------


def _footer_column(title: str = "Rechtliches") -> FooterColumn:
    """Helper: gueltige FooterColumn fuer FooterInput-Tests."""
    return FooterColumn(
        title=title, links=[FooterLink(label="Impressum", href="/impressum")]
    )


class TestFooterInput:
    def test_minimal_valid(self):
        inp = FooterInput(columns=[_footer_column()])
        assert inp.version is None  # Default
        assert inp.note is None  # Default

    def test_all_fields(self):
        inp = FooterInput(
            columns=[_footer_column()],
            version="v0.8.0",
            note="(c) 2026 Matthias Nitsche",
        )
        assert inp.version == "v0.8.0"

    def test_columns_min_length(self):
        """columns: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            FooterInput(columns=[])

    def test_columns_max_length(self):
        """columns: max 3 — die vierte Spalte wird abgelehnt."""
        three = [_footer_column(f"Spalte {i}") for i in range(3)]
        FooterInput(columns=three)  # genau 3 ist gueltig
        with pytest.raises(ValidationError):
            FooterInput(columns=[*three, _footer_column("Spalte 4")])

    def test_frozen(self):
        inp = FooterInput(columns=[_footer_column()])
        with pytest.raises(ValidationError):
            inp.version = "v9.9.9"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            FooterInput(columns=[_footer_column()], foo="bar")


# ---------------------------------------------------------------------------
# ContentCardInput
# ---------------------------------------------------------------------------


class TestContentCardInput:
    def test_minimal_valid(self):
        inp = ContentCardInput(title="Reisetagebuch", body="Eintraege aus 2026.")
        assert inp.href is None  # Default
        assert inp.tier is None  # Default

    def test_all_fields(self):
        inp = ContentCardInput(
            title="Reisetagebuch",
            body="Eintraege aus 2026.",
            href="/atelier/reisen",
            tier=WebTier.ATELIER,
        )
        assert inp.tier is WebTier.ATELIER

    def test_title_min_length(self):
        with pytest.raises(ValidationError):
            ContentCardInput(title="", body="Text")

    def test_body_min_length(self):
        with pytest.raises(ValidationError):
            ContentCardInput(title="Titel", body="")

    def test_frozen(self):
        inp = ContentCardInput(title="Reisetagebuch", body="Eintraege.")
        with pytest.raises(ValidationError):
            inp.title = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            ContentCardInput(title="Titel", body="Text", foo="bar")


# ---------------------------------------------------------------------------
# CardGridInput
# ---------------------------------------------------------------------------


def _content_card(title: str = "Karte") -> ContentCardInput:
    """Helper: gueltige ContentCardInput fuer CardGridInput-Tests."""
    return ContentCardInput(title=title, body="Karten-Text.")


class TestCardGridInput:
    def test_minimal_valid(self):
        inp = CardGridInput(cards=[_content_card()])
        assert inp.columns == 3  # Default

    def test_all_fields(self):
        inp = CardGridInput(cards=[_content_card("A"), _content_card("B")], columns=2)
        assert inp.columns == 2

    def test_cards_min_length(self):
        """cards: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            CardGridInput(cards=[])

    def test_columns_ge_1(self):
        """columns: >= 1 — 0 wird abgelehnt."""
        with pytest.raises(ValidationError):
            CardGridInput(cards=[_content_card()], columns=0)

    def test_columns_le_4(self):
        """columns: <= 4 — 5 wird abgelehnt."""
        with pytest.raises(ValidationError):
            CardGridInput(cards=[_content_card()], columns=5)

    def test_columns_bounds_valid(self):
        """columns: 1 und 4 (Grenzwerte) sind gueltig."""
        CardGridInput(cards=[_content_card()], columns=1)
        CardGridInput(cards=[_content_card()], columns=4)

    def test_frozen(self):
        inp = CardGridInput(cards=[_content_card()])
        with pytest.raises(ValidationError):
            inp.columns = 4

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            CardGridInput(cards=[_content_card()], foo="bar")
