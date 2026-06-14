"""Verhaltens-Tests fuer die 9 Web-Tier-Contracts (UX-Welle v0.2).

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
    CardGridInput,
    ContentCardInput,
    EmptyStateInput,
    FooterInput,
    FooterLink,
    FooterSegment,
    NewsItemDetail,
    NewsItemInput,
    PageHeaderInput,
    SourceLink,
    SourceRefInput,
    SubNavInput,
    SubNavTab,
    TierChipInput,
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
# EmptyStateInput
# ---------------------------------------------------------------------------


class TestEmptyStateInput:
    def test_valid_minimal(self):
        e = EmptyStateInput(message="Sobald Einträge da sind, erscheinen sie hier.")
        assert e.tier is None

    def test_valid_with_tier(self):
        e = EmptyStateInput(message="x", tier=WebTier.ATELIER)
        assert e.tier is WebTier.ATELIER

    def test_message_min_length(self):
        with pytest.raises(ValidationError):
            EmptyStateInput(message="")

    def test_frozen(self):
        e = EmptyStateInput(message="x")
        with pytest.raises(ValidationError):
            e.message = "y"

    def test_extra_forbid(self):
        with pytest.raises(ValidationError):
            EmptyStateInput(message="x", unbekannt=1)


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
# FooterSegment
# ---------------------------------------------------------------------------


class TestFooterSegment:
    def test_minimal_valid(self):
        seg = FooterSegment(text="mkn-desk.com")
        assert seg.text == "mkn-desk.com"
        assert seg.slot_id is None  # Default

    def test_text_min_length(self):
        with pytest.raises(ValidationError):
            FooterSegment(text="")

    def test_slot_id_accepts_string(self):
        """Ein Segment mit slot_id wird zum client-seitigen Hydration-Slot."""
        seg = FooterSegment(text="Profil …", slot_id="footer-user-info")
        assert seg.slot_id == "footer-user-info"

    def test_frozen(self):
        seg = FooterSegment(text="mkn-desk.com")
        with pytest.raises(ValidationError):
            seg.text = "geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            FooterSegment(text="X", foo="bar")


# ---------------------------------------------------------------------------
# FooterInput
# ---------------------------------------------------------------------------


def _segment(text: str = "mkn-desk.com") -> FooterSegment:
    """Helper: gueltiges FooterSegment fuer FooterInput-Tests."""
    return FooterSegment(text=text)


def _link(label: str = "Impressum") -> FooterLink:
    """Helper: gueltiger FooterLink fuer FooterInput-Tests."""
    return FooterLink(label=label, href="/impressum")


class TestFooterInput:
    def test_minimal_valid(self):
        inp = FooterInput(segments=[_segment()], links=[_link()])
        assert inp.version is None  # Default

    def test_all_fields(self):
        inp = FooterInput(
            segments=[_segment(), _segment("Atelier · AMBER")],
            links=[_link(), _link("Datenschutz")],
            version="v0.2.1",
        )
        assert inp.version == "v0.2.1"
        assert len(inp.segments) == 2

    def test_segments_min_length(self):
        """segments: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            FooterInput(segments=[], links=[_link()])

    def test_links_min_length(self):
        """links: mind. 1 — leere Liste wird abgelehnt."""
        with pytest.raises(ValidationError):
            FooterInput(segments=[_segment()], links=[])

    def test_frozen(self):
        inp = FooterInput(segments=[_segment()], links=[_link()])
        with pytest.raises(ValidationError):
            inp.version = "v9.9.9"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            FooterInput(segments=[_segment()], links=[_link()], foo="bar")

    def test_segment_with_slot(self):
        """Ein Segment der Identitaets-Zeile kann einen Hydration-Slot tragen."""
        inp = FooterInput(
            segments=[_segment(), FooterSegment(text="Profil …", slot_id="x")],
            links=[_link()],
        )
        assert inp.segments[1].slot_id == "x"


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


# ---------------------------------------------------------------------------
# SourceLink
# ---------------------------------------------------------------------------


class TestSourceLink:
    def test_minimal_valid(self):
        link = SourceLink(href="https://euronews.com", label="euronews.com")
        assert link.label == "euronews.com"

    def test_href_min_length(self):
        with pytest.raises(ValidationError):
            SourceLink(href="", label="x")

    def test_label_min_length(self):
        with pytest.raises(ValidationError):
            SourceLink(href="/x", label="")

    def test_frozen(self):
        link = SourceLink(href="/x", label="x")
        with pytest.raises(ValidationError):
            link.label = "y"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            SourceLink(href="/x", label="x", foo="bar")


# ---------------------------------------------------------------------------
# SourceRefInput
# ---------------------------------------------------------------------------


def _source_link(label: str = "euronews.com") -> SourceLink:
    """Helper: gueltiger SourceLink fuer Source-Ref-Tests."""
    return SourceLink(href="https://example.com", label=label)


class TestSourceRefInput:
    def test_minimal_valid(self):
        ref = SourceRefInput(primary=_source_link())
        assert ref.weitere == []  # Default: leere Liste

    def test_with_weitere(self):
        ref = SourceRefInput(
            primary=_source_link("a"),
            weitere=[_source_link("b"), _source_link("c")],
        )
        assert len(ref.weitere) == 2

    def test_default_weitere_is_independent(self):
        """Default-Liste darf nicht zwischen Instanzen geteilt werden."""
        a = SourceRefInput(primary=_source_link())
        b = SourceRefInput(primary=_source_link())
        assert a.weitere is not b.weitere

    def test_primary_required(self):
        with pytest.raises(ValidationError):
            SourceRefInput(weitere=[_source_link()])

    def test_frozen(self):
        ref = SourceRefInput(primary=_source_link())
        with pytest.raises(ValidationError):
            ref.primary = _source_link("other")

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            SourceRefInput(primary=_source_link(), foo="bar")


# ---------------------------------------------------------------------------
# NewsItemDetail
# ---------------------------------------------------------------------------


class TestNewsItemDetail:
    def test_minimal_valid(self):
        d = NewsItemDetail(level_label="Detailliert", text="Vertiefung.")
        assert d.sources is None  # Default
        assert d.summary_label == "mehr"  # Default

    def test_all_fields(self):
        d = NewsItemDetail(
            level_label="Medium · Lagebericht",
            text="Vertiefung.",
            sources=SourceRefInput(primary=_source_link()),
            summary_label="medium",
        )
        assert d.summary_label == "medium"
        assert d.sources is not None

    def test_level_label_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemDetail(level_label="", text="x")

    def test_text_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemDetail(level_label="L", text="")

    def test_summary_label_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemDetail(level_label="L", text="x", summary_label="")

    def test_frozen(self):
        d = NewsItemDetail(level_label="L", text="x")
        with pytest.raises(ValidationError):
            d.text = "y"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            NewsItemDetail(level_label="L", text="x", foo="bar")


# ---------------------------------------------------------------------------
# NewsItemInput
# ---------------------------------------------------------------------------


class TestNewsItemInput:
    def test_minimal_valid(self):
        item = NewsItemInput(
            title="Schlagzeile",
            text="Basis-Tiefe.",
            kategorie="Politik",
            zeitangabe="vor 3 Std",
        )
        assert item.rank is None
        assert item.eyebrow is None
        assert item.is_aufmacher is False
        assert item.deeper_href is None
        assert item.source is None
        assert item.detail is None

    def test_all_fields(self):
        item = NewsItemInput(
            rank="01",
            eyebrow="Aufmacher · stand auf S1",
            is_aufmacher=True,
            title="Schlagzeile",
            deeper_href="#fin-aufmacher",
            text="Basis-Tiefe.",
            kategorie="Finanzen",
            zeitangabe="vor 4 Std",
            source=SourceRefInput(primary=_source_link()),
            detail=NewsItemDetail(level_label="Detailliert", text="Mehr."),
        )
        assert item.is_aufmacher is True
        assert item.deeper_href == "#fin-aufmacher"
        assert item.detail is not None

    def test_title_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemInput(title="", text="x", kategorie="K", zeitangabe="Z")

    def test_text_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemInput(title="T", text="", kategorie="K", zeitangabe="Z")

    def test_kategorie_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemInput(title="T", text="x", kategorie="", zeitangabe="Z")

    def test_zeitangabe_min_length(self):
        with pytest.raises(ValidationError):
            NewsItemInput(title="T", text="x", kategorie="K", zeitangabe="")

    def test_frozen(self):
        item = NewsItemInput(title="T", text="x", kategorie="K", zeitangabe="Z")
        with pytest.raises(ValidationError):
            item.title = "Geaendert"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            NewsItemInput(title="T", text="x", kategorie="K", zeitangabe="Z", foo="bar")
