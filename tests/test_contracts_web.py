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

from datetime import date, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    CardGridInput,
    ContentCardInput,
    EmptyStateInput,
    FooterInput,
    FooterLink,
    FooterSegment,
    PageHeaderInput,
    SubNavInput,
    SubNavTab,
    TierChipInput,
    VerlaufChartInput,
    VerlaufMarkierung,
    VerlaufPunkt,
    VerlaufReihe,
    WebTier,
    ZeitraumLeisteInput,
    ZeitraumOption,
)

# ---------------------------------------------------------------------------
# WebTier (Enum)
# ---------------------------------------------------------------------------


class TestWebTier:
    """str-Enum der sieben Web-Tier von mkn-desk.com."""

    def test_valid_values(self):
        assert WebTier.BIBLIOTHEK.value == "bibliothek"
        assert WebTier.ATELIER.value == "atelier"
        assert WebTier.KABINETT.value == "kabinett"
        assert WebTier.START.value == "start"
        assert WebTier.OBSERVATORIUM.value == "observatorium"
        assert WebTier.MAGAZIN.value == "magazin"
        assert WebTier.ARCHIV.value == "archiv"

    def test_member_count(self):
        """Genau sieben Tier (0.20.0: magazin kommt neben archiv zurueck, Erweitern)."""
        assert len(WebTier) == 7

    def test_webtier_magazin_existiert_neben_archiv(self):
        assert WebTier("magazin") is WebTier.MAGAZIN
        assert WebTier("archiv") is WebTier.ARCHIV
        assert WebTier.MAGAZIN is not WebTier.ARCHIV

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
# Verlauf-Chart (0.17.0): VerlaufPunkt / VerlaufReihe / VerlaufMarkierung /
# VerlaufChartInput
# ---------------------------------------------------------------------------


def _reihe(label: str = "Gewicht", punkte: list[VerlaufPunkt] | None = None):
    """Helper: gueltige Reihe (Default: zwei erfundene Tageswerte)."""
    if punkte is None:
        punkte = [
            VerlaufPunkt(t=date(2026, 10, 15), wert=80.0),
            VerlaufPunkt(t=date(2026, 10, 16), wert=79.5),
        ]
    return VerlaufReihe(label=label, punkte=punkte)


def _chart(**overrides) -> VerlaufChartInput:
    base = {
        "titel": "Gewicht",
        "einheit": "kg",
        "reihen": [_reihe()],
        "von": date(2026, 10, 1),
        "bis": date(2026, 10, 17),
    }
    base.update(overrides)
    return VerlaufChartInput(**base)


class TestVerlaufPunkt:
    def test_datum_wird_akzeptiert(self):
        p = VerlaufPunkt(t=date(2026, 10, 17), wert=1.5)
        assert p.t == date(2026, 10, 17)
        assert not isinstance(p.t, datetime)

    def test_datum_als_iso_string(self):
        assert VerlaufPunkt(t="2026-10-17", wert=1).t == date(2026, 10, 17)

    def test_zeitpunkt_als_iso_string(self):
        p = VerlaufPunkt(t="2026-10-17T06:30:00", wert=1)
        assert isinstance(p.t, datetime)

    def test_datetime_ohne_zone_ist_berlin(self):
        """Oktober (MESZ): Berlin ist UTC+2 — ein naives datetime wird so gelesen."""
        p = VerlaufPunkt(t=datetime(2026, 10, 17, 6, 30), wert=1)  # noqa: DTZ001 - naiv ist der Pruefgegenstand
        assert p.t.utcoffset() == timedelta(hours=2)

    def test_datetime_ohne_zone_ist_berlin_im_winter(self):
        """Januar (MEZ): UTC+1 — echte Zone, kein fester Versatz."""
        p = VerlaufPunkt(t=datetime(2026, 1, 17, 6, 30), wert=1)  # noqa: DTZ001 - naiv ist der Pruefgegenstand
        assert p.t.utcoffset() == timedelta(hours=1)

    def test_datetime_mit_zone_bleibt_unveraendert(self):
        t = datetime(2026, 10, 17, 6, 30, tzinfo=timezone.utc)
        assert VerlaufPunkt(t=t, wert=1).t == t
        assert VerlaufPunkt(t=t, wert=1).t.utcoffset() == timedelta(0)

    def test_wert_nan_und_inf_abgelehnt(self):
        """JSON kennt kein NaN/Infinity — der Block im HTML waere nicht parsebar."""
        for schlecht in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(ValidationError):
                VerlaufPunkt(t=date(2026, 10, 17), wert=schlecht)

    def test_wert_pflicht(self):
        with pytest.raises(ValidationError):
            VerlaufPunkt(t=date(2026, 10, 17))

    def test_frozen(self):
        p = VerlaufPunkt(t=date(2026, 10, 17), wert=1)
        with pytest.raises(ValidationError):
            p.wert = 2

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            VerlaufPunkt(t=date(2026, 10, 17), wert=1, foo="bar")


class TestVerlaufReihe:
    def test_minimal_valid(self):
        r = VerlaufReihe(label="Ruhepuls", punkte=[])
        assert r.art == "messung"  # Default

    def test_punkte_duerfen_leer_sein(self):
        """Eine Reihe ohne Punkte ist gueltig — die Achse steht auch ohne Daten."""
        assert VerlaufReihe(label="X", punkte=[]).punkte == []

    def test_art_gleitend(self):
        assert VerlaufReihe(label="7-Tage", punkte=[], art="gleitend").art == "gleitend"

    def test_art_ungueltig(self):
        with pytest.raises(ValidationError):
            VerlaufReihe(label="X", punkte=[], art="trend")

    def test_achse_default_links(self):
        """0.18.0: ohne Angabe liegt die Reihe links (wie bis 0.17.0)."""
        assert VerlaufReihe(label="X", punkte=[]).achse == "links"

    @pytest.mark.parametrize("achse", ["links", "rechts"])
    def test_achse_gueltig(self, achse):
        assert VerlaufReihe(label="X", punkte=[], achse=achse).achse == achse

    @pytest.mark.parametrize("achse", ["oben", "rechts ", "Links", "", None])
    def test_achse_ungueltig(self, achse):
        with pytest.raises(ValidationError):
            VerlaufReihe(label="X", punkte=[], achse=achse)

    def test_label_grenzen(self):
        VerlaufReihe(label="a", punkte=[])
        VerlaufReihe(label="a" * 40, punkte=[])
        with pytest.raises(ValidationError):
            VerlaufReihe(label="", punkte=[])
        with pytest.raises(ValidationError):
            VerlaufReihe(label="a" * 41, punkte=[])

    def test_frozen(self):
        r = VerlaufReihe(label="X", punkte=[])
        with pytest.raises(ValidationError):
            r.label = "Y"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            VerlaufReihe(label="X", punkte=[], foo="bar")


class TestVerlaufMarkierung:
    def test_minimal_valid(self):
        m = VerlaufMarkierung(t=date(2026, 10, 10), label="Lauf")
        assert m.label == "Lauf"

    def test_datetime_ohne_zone_ist_berlin(self):
        m = VerlaufMarkierung(t=datetime(2026, 10, 10, 8, 0), label="Lauf")  # noqa: DTZ001 - naiv ist der Pruefgegenstand
        assert m.t.utcoffset() == timedelta(hours=2)

    def test_label_grenzen(self):
        VerlaufMarkierung(t=date(2026, 10, 10), label="a" * 30)
        with pytest.raises(ValidationError):
            VerlaufMarkierung(t=date(2026, 10, 10), label="")
        with pytest.raises(ValidationError):
            VerlaufMarkierung(t=date(2026, 10, 10), label="a" * 31)

    def test_frozen(self):
        m = VerlaufMarkierung(t=date(2026, 10, 10), label="Lauf")
        with pytest.raises(ValidationError):
            m.label = "Andere"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            VerlaufMarkierung(t=date(2026, 10, 10), label="Lauf", foo="bar")


class TestVerlaufChartInput:
    def test_minimal_valid_defaults(self):
        c = _chart()
        assert c.zielband_min is None and c.zielband_max is None
        assert c.markierungen == []
        assert c.dezimalstellen == 1
        assert c.hoehe == 260
        assert c.beschreibung is None

    def test_reihen_leer_abgelehnt(self):
        with pytest.raises(ValidationError):
            _chart(reihen=[])

    def test_erste_reihe_liegt_links(self):
        """Die erste Reihe traegt Zielband, Marken und Beschreibung — beides haengt
        an der linken Achse; liegt sie rechts, stuende das Band auf der falschen Skala."""
        rechts = VerlaufReihe(label="Summe", punkte=[], achse="rechts")
        with pytest.raises(ValidationError, match="erste Reihe"):
            _chart(reihen=[rechts, _reihe("Tag")])

    def test_weitere_reihen_duerfen_rechts_liegen(self):
        rechts = VerlaufReihe(label="Summe", punkte=[], achse="rechts")
        c = _chart(reihen=[_reihe("Tag"), rechts])
        assert [r.achse for r in c.reihen] == ["links", "rechts"]

    def test_eine_einzige_reihe_rechts_ist_abgelehnt(self):
        rechts = VerlaufReihe(label="Summe", punkte=[], achse="rechts")
        with pytest.raises(ValidationError, match="erste Reihe"):
            _chart(reihen=[rechts])

    def test_reihen_grenzen(self):
        _chart(reihen=[_reihe(f"R{i}") for i in range(4)])
        with pytest.raises(ValidationError):
            _chart(reihen=[_reihe(f"R{i}") for i in range(5)])

    def test_von_muss_vor_bis_liegen(self):
        with pytest.raises(ValidationError, match="von muss vor bis liegen"):
            _chart(von=date(2026, 10, 17), bis=date(2026, 10, 17))
        with pytest.raises(ValidationError, match="von muss vor bis liegen"):
            _chart(von=date(2026, 10, 18), bis=date(2026, 10, 17))

    def test_zielband_beide_oder_keins(self):
        _chart(zielband_min=70.0, zielband_max=80.0)
        with pytest.raises(ValidationError, match="Zielband"):
            _chart(zielband_min=70.0)
        with pytest.raises(ValidationError, match="Zielband"):
            _chart(zielband_max=80.0)

    def test_zielband_min_nicht_ueber_max(self):
        _chart(zielband_min=75.0, zielband_max=75.0)  # Grenzfall: gleich ist gueltig
        with pytest.raises(ValidationError, match="Zielband"):
            _chart(zielband_min=80.0, zielband_max=70.0)

    def test_zielband_nan_abgelehnt(self):
        with pytest.raises(ValidationError):
            _chart(zielband_min=float("nan"), zielband_max=80.0)

    def test_markierungen_grenzen(self):
        m = [VerlaufMarkierung(t=date(2026, 10, 2), label=f"M{i}") for i in range(12)]
        assert len(_chart(markierungen=m).markierungen) == 12
        with pytest.raises(ValidationError):
            _chart(markierungen=[*m, VerlaufMarkierung(t=date(2026, 10, 3), label="X")])

    def test_dezimalstellen_grenzen(self):
        for n in (0, 1, 2, 3):
            assert _chart(dezimalstellen=n).dezimalstellen == n
        for n in (-1, 4):
            with pytest.raises(ValidationError):
                _chart(dezimalstellen=n)

    def test_hoehe_nur_stufen(self):
        for h in (180, 220, 260, 320, 400, 600):
            assert _chart(hoehe=h).hoehe == h
        with pytest.raises(ValidationError):
            _chart(hoehe=300)

    def test_titel_grenzen(self):
        _chart(titel="a" * 80)
        with pytest.raises(ValidationError):
            _chart(titel="")
        with pytest.raises(ValidationError):
            _chart(titel="a" * 81)

    def test_einheit_grenzen(self):
        _chart(einheit="")  # Einheit darf leer sein (z.B. Verhaeltniszahl)
        _chart(einheit="a" * 16)
        with pytest.raises(ValidationError):
            _chart(einheit="a" * 17)

    def test_frozen(self):
        c = _chart()
        with pytest.raises(ValidationError):
            c.titel = "Anders"

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            _chart(farbe="#ff0000")

    # --- beschreibung_text(): Default fuer aria-label ----------------------

    def test_beschreibung_default_nennt_titel_einheit_letztstand_zeitraum(self):
        text = _chart().beschreibung_text()
        assert "Gewicht" in text
        assert "kg" in text
        assert "79,5" in text  # Letztstand der ersten Reihe, deutsches Komma
        assert "16.10.2026" in text  # Datum des Letztstands
        assert "01.10.2026" in text and "17.10.2026" in text  # Zeitraum

    def test_beschreibung_default_rundet_mit_dezimalstellen(self):
        reihe = _reihe(punkte=[VerlaufPunkt(t=date(2026, 10, 16), wert=79.456)])
        assert "79,46" in _chart(reihen=[reihe], dezimalstellen=2).beschreibung_text()
        assert "79" in _chart(reihen=[reihe], dezimalstellen=0).beschreibung_text()

    def test_beschreibung_default_tausendertrenner(self):
        reihe = _reihe(punkte=[VerlaufPunkt(t=date(2026, 10, 16), wert=12345.0)])
        text = _chart(reihen=[reihe], einheit="Anzahl", dezimalstellen=0)
        assert "12.345" in text.beschreibung_text()

    def test_beschreibung_default_letztstand_ist_juengster_punkt(self):
        """Nicht der zuletzt genannte, sondern der zeitlich juengste Punkt."""
        reihe = _reihe(
            punkte=[
                VerlaufPunkt(t=date(2026, 10, 16), wert=79.5),
                VerlaufPunkt(t=date(2026, 10, 3), wert=90.0),
            ]
        )
        assert "79,5" in _chart(reihen=[reihe]).beschreibung_text()

    def test_beschreibung_default_ohne_punkte(self):
        text = _chart(reihen=[_reihe(punkte=[])]).beschreibung_text()
        assert "keine Werte" in text
        assert "Gewicht" in text

    def test_beschreibung_explizit_gewinnt(self):
        assert _chart(beschreibung="Eigener Text").beschreibung_text() == "Eigener Text"


# ---------------------------------------------------------------------------
# ZeitraumOption / ZeitraumLeisteInput (0.18.0)
# ---------------------------------------------------------------------------


def _optionen(aktiv: int | None = 0) -> list[ZeitraumOption]:
    namen = [("30 Tage", "?tage=30"), ("90 Tage", "?tage=90"), ("1 Jahr", "?tage=365")]
    return [
        ZeitraumOption(label=label, href=href, active=i == aktiv)
        for i, (label, href) in enumerate(namen)
    ]


class TestZeitraumOption:
    def test_minimal(self):
        o = ZeitraumOption(label="30 Tage", href="?tage=30")
        assert o.active is False

    def test_active(self):
        assert ZeitraumOption(label="X", href="?x", active=True).active is True

    def test_label_und_href_sind_pflicht(self):
        with pytest.raises(ValidationError):
            ZeitraumOption(label="", href="?x")
        with pytest.raises(ValidationError):
            ZeitraumOption(label="X", href="")

    def test_frozen_und_extra_forbid(self):
        o = ZeitraumOption(label="X", href="?x")
        with pytest.raises(ValidationError):
            o.label = "Y"
        with pytest.raises(ValidationError):
            ZeitraumOption(label="X", href="?x", foo="bar")


class TestZeitraumLeisteInput:
    def test_gueltig_mit_drei_optionen(self):
        inp = ZeitraumLeisteInput(optionen=_optionen())
        assert len(inp.optionen) == 3
        assert inp.aria_label == "Zeitraum"

    def test_eine_option_ist_keine_auswahl(self):
        with pytest.raises(ValidationError):
            ZeitraumLeisteInput(optionen=_optionen()[:1])

    def test_zu_viele_optionen_werden_abgelehnt(self):
        zu_viele = [
            ZeitraumOption(label=str(i), href=f"?tage={i}") for i in range(1, 8)
        ]
        with pytest.raises(ValidationError):
            ZeitraumLeisteInput(optionen=zu_viele)

    def test_sechs_optionen_sind_gueltig(self):
        sechs = [ZeitraumOption(label=str(i), href=f"?tage={i}") for i in range(1, 7)]
        assert len(ZeitraumLeisteInput(optionen=sechs).optionen) == 6

    def test_keine_aktive_option_ist_gueltig(self):
        """?tage=7 steht in keiner Option: der Konsument markiert dann keine."""
        inp = ZeitraumLeisteInput(optionen=_optionen(aktiv=None))
        assert not any(o.active for o in inp.optionen)

    def test_zwei_aktive_optionen_werden_abgelehnt(self):
        optionen = _optionen(aktiv=0)
        optionen[1] = ZeitraumOption(label="90 Tage", href="?tage=90", active=True)
        with pytest.raises(ValidationError, match="aktiv"):
            ZeitraumLeisteInput(optionen=optionen)

    def test_aria_label_ist_pflichtig_nicht_leer(self):
        with pytest.raises(ValidationError):
            ZeitraumLeisteInput(optionen=_optionen(), aria_label="")

    def test_frozen_und_extra_forbid(self):
        inp = ZeitraumLeisteInput(optionen=_optionen())
        with pytest.raises(ValidationError):
            inp.aria_label = "X"
        with pytest.raises(ValidationError):
            ZeitraumLeisteInput(optionen=_optionen(), foo="bar")
