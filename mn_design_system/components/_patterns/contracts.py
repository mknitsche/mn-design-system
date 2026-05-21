"""Pydantic-Contracts fuer Komponenten-Inputs (Welle B v0.2.0).

Maschinen-lesbare API-Definitionen. Renderer-Implementierungen (pdf/, web/, latex/)
muessen diese als Eingabe akzeptieren — Mismatch wird beim Konstruktor sichtbar.

Begruendung (Gemini-Befund 5 v1.1->v1.2): Markdown-Specs allein sind menschlich
lesbar, aber nicht maschinell ueberpruefbar. Pydantic erzwingt Typ-Konsistenz
zwischen Spec und Implementation.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Sparkline
# ---------------------------------------------------------------------------


class SparklineInput(BaseModel):
    """API-Contract fuer build_sparkline().

    values: Zeitreihe, chronologisch (alt -> neu). Mindestens 2 Werte.
    width / height: Zielgroesse in Points.
    color: optionaler Hex-String oder None (dann Default-H2-Farbe).
    """

    model_config = {"extra": "forbid", "frozen": True}

    values: list[float] = Field(min_length=2)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    color: str | None = None  # Hex-Format wie "#4338ca" oder None


# ---------------------------------------------------------------------------
# KPI-Card
# ---------------------------------------------------------------------------


class KpiTrendDirection(str, Enum):
    """Trend-Richtung fuer KPI-Delta."""

    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class KpiCardInput(BaseModel):
    """API-Contract fuer build_kpi_card().

    label: Kicker-Text (z.B. "DAX")
    value: Hauptwert formatiert (z.B. "22.450")
    change_pct: optional, prozentuale Veraenderung (positiv/negativ/null)
    sparkline_values: optional Zeitreihe fuer kleine Trend-Linie
    caption: optional Untertitel-Text (z.B. "30 Tage")
    """

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1)
    value: str = Field(min_length=1)
    change_pct: float | None = None
    sparkline_values: list[float] | None = None
    caption: str | None = None

    def trend_direction(self) -> KpiTrendDirection:
        """Abgeleiteter Trend aus change_pct.

        v0.4.1 (S239 B5): Schwellwert von 0.01 auf 0.5 hochgezogen — KT-1
        Briefing-Befund 30.04.: kleine Bewegungen (<0.5%) sollen nicht
        rot/gruen markiert werden, sondern neutral (grau, color.viz.muted).
        """
        if self.change_pct is None or abs(self.change_pct) < 0.5:
            return KpiTrendDirection.NEUTRAL
        return KpiTrendDirection.UP if self.change_pct > 0 else KpiTrendDirection.DOWN


# ---------------------------------------------------------------------------
# Wetter-Strip
# ---------------------------------------------------------------------------


class WetterCategory(str, Enum):
    """Wetter-Kategorien (mappen auf Phosphor-Icons)."""

    SONNIG = "sonnig"
    HEITER = "heiter"
    BEWOELKT = "bewoelkt"
    REGEN = "regen"
    SCHNEE = "schnee"
    GEWITTER = "gewitter"
    NEBEL = "nebel"
    WIND = "wind"


class WetterDay(BaseModel):
    """Einzelner Tag im Wetter-Strip."""

    model_config = {"extra": "forbid", "frozen": True}

    header_label: str = Field(min_length=1, max_length=15)
    """Spalten-Header-Text. Beispiele: 'Heute', 'Mi', 'Mi 30.04.'."""

    category: WetterCategory
    temp_min_c: int
    temp_max_c: int
    precip_pct: int = Field(ge=0, le=100)


class WetterStripInput(BaseModel):
    """API-Contract fuer build_wetter_strip().

    days: 3-5 Tage, chronologisch ab heute.
    summary_text: optional, kurzer Erzaehl-Satz (z.B. von Wetterochs).
    location: Standort-Name fuer Header (z.B. "Nuernberg").
    """

    model_config = {"extra": "forbid", "frozen": True}

    days: list[WetterDay] = Field(min_length=3, max_length=5)
    summary_text: str | None = None
    location: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# Web-Tier-Komponenten (UX-Welle v0.2)
# ---------------------------------------------------------------------------


class WebTier(str, Enum):
    """Die vier Web-Tier von mkn-desk.com. Mappt auf color.tier.<tier>.*."""

    BIBLIOTHEK = "bibliothek"
    ATELIER = "atelier"
    KABINETT = "kabinett"
    START = "start"


class TierChipInput(BaseModel):
    """API-Contract fuer render_tier_chip_html(). Primitiv-Baustein.

    tier: Farb-Familie (color.tier.<tier>.*).
    label: sichtbarer Text.
    bordered: True = L2-Status-Chip (Brand-Bar, mit Border, nicht klickbar).
              False = L3-Auswahl-Chip (Sub-Nav, Background-only).
    """

    model_config = {"extra": "forbid", "frozen": True}

    tier: WebTier
    label: str = Field(min_length=1)
    bordered: bool = True


class SubNavTab(BaseModel):
    """Ein Tab in der Sub-Nav."""

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1)
    href: str = Field(min_length=1)
    active: bool = False


class SubNavInput(BaseModel):
    """L3 — Auswahl-Navigation INNERHALB eines Tiers (Spec §A5/A6).

    tier: Tier-Kontext der gesamten Sub-Nav (alle Tabs in-tier).
    tabs: mind. 1 Tab. Genau einer sollte active=True sein.
    aria_label: Landmark-Label des <nav> (Barrierefreiheit, WCAG 2.4.1).
                Mehrere <nav> pro Seite (L1 Top-Nav + L3 Sub-Nav) muessen
                unterscheidbar sein — der Konsument kann ein praeziseres
                Label setzen (z.B. "Bibliothek-Bereiche").
    """

    model_config = {"extra": "forbid", "frozen": True}

    tier: WebTier
    tabs: list[SubNavTab] = Field(min_length=1)
    aria_label: str = Field(default="Bereichs-Navigation", min_length=1)


class PageHeaderInput(BaseModel):
    """Seiten-Kopf: H1 + optionaler Lead-Absatz."""

    model_config = {"extra": "forbid", "frozen": True}

    title: str = Field(min_length=1)
    lead: str | None = None


class FooterLink(BaseModel):
    """Ein Link im rechten Cluster der Footer-Schlusszeile."""

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1)
    href: str = Field(min_length=1)


class FooterSegment(BaseModel):
    """Ein Segment der linken Identitaets-Zeile.

    Segmente werden in der Renderung mit einem `|`-Strich getrennt. Ist
    `slot_id` gesetzt, wird das Segment zu einem client-seitig gefuellten
    Hydration-Slot (z.B. Profil-Info aus /api/me); sonst ist es statischer Text.
    """

    model_config = {"extra": "forbid", "frozen": True}

    text: str = Field(min_length=1)
    slot_id: str | None = None


class FooterInput(BaseModel):
    """Schlanke einzeilige Seiten-Fusszeile (Spec §cld1-S19 / cld1-S21).

    Links eine Identitaets-Zeile aus `|`-getrennten Segmenten, rechts die
    Rechtslinks (`·`-getrennt) plus optionale Version. Tier-neutral — auf
    jeder Seite identisch.
    """

    model_config = {"extra": "forbid", "frozen": True}

    segments: list[FooterSegment] = Field(min_length=1)
    links: list[FooterLink] = Field(min_length=1)
    version: str | None = None


class ContentCardInput(BaseModel):
    """Generische Inhalts-Karte (Titel + Text, optional verlinkt + tier-getoent).

    title: Karten-Titel; wird zum Link-Text, wenn href gesetzt ist.
    body: Karten-Text.
    href: optionales Ziel — gesetzt macht die Karte klickbar (Titel als <a>).
    tier: optionale Tier-Familie; setzt die Akzent-Border (color.tier.<tier>.border).
    """

    model_config = {"extra": "forbid", "frozen": True}

    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    href: str | None = None
    tier: WebTier | None = None


class CardGridInput(BaseModel):
    """Responsives Karten-Raster.

    cards: mind. 1 Content-Card.
    columns: Spaltenzahl 1-4 (Default 3) — landet als CSS-Variable
             --mn-card-grid-cols, kein Hex.
    """

    model_config = {"extra": "forbid", "frozen": True}

    cards: list[ContentCardInput] = Field(min_length=1)
    columns: int = Field(default=3, ge=1, le=4)


class EmptyStateInput(BaseModel):
    """Ruhiger Leer-Zustand — "hier erscheint bald etwas", kein Baustellen-Schild.

    message: sichtbarer Hinweistext.
    tier:    optionale Tier-Familie für eine zarte farbliche Verankerung.
    """

    model_config = {"extra": "forbid", "frozen": True}

    message: str = Field(min_length=1)
    tier: WebTier | None = None


# ---------------------------------------------------------------------------
# Masthead (Web-Foundation, Design §10) — loest TopNav + BrandBar ab
# ---------------------------------------------------------------------------


class MastheadEmblem(BaseModel):
    """Hirn-Emblem links im Masthead, verlinkt (Home-Ruecksprung).

    src: Bild-URL (z.B. "/assets/logo-mkn2ndbrain-kopf.png").
    alt: Alt-Text fuer Screenreader.
    href: Ziel des Emblem-Links (z.B. "/start/").
    """

    model_config = {"extra": "forbid", "frozen": True}

    src: str = Field(min_length=1)
    alt: str = Field(min_length=1)
    href: str = Field(min_length=1)


class MastheadTierItem(BaseModel):
    """Ein Tier-Pill in Reihe 2 des Masthead (= ein Tier-Ziel)."""

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1)
    href: str = Field(min_length=1)
    tier: WebTier
    active: bool = False


class MastheadChip(BaseModel):
    """Kontext-Chip rechts in Reihe 2 (z.B. Page-Tier 'Atelier · AMBER')."""

    model_config = {"extra": "forbid", "frozen": True}

    tier: WebTier
    label: str = Field(min_length=1)


class MastheadInput(BaseModel):
    """Editorialer Masthead (Design §10) — dunkler Kopf, zwei Reihen.

    Reihe 1 (Identitaet): Emblem + Wortmarke + optionales Editions-Datum.
    Reihe 2 (Tier-Navigation): Tier-Pills links, optionaler Kontext-Chip
    rechts, optional ein client-seitig gefuellter Hydration-Chip.

    Das helle Lokal-Band (reine Sub-Navigation) ist NICHT Teil des Masthead —
    es ist die separat gerenderte sub_nav-Komponente darunter.
    """

    model_config = {"extra": "forbid", "frozen": True}

    emblem: MastheadEmblem
    wordmark: str = Field(min_length=1)
    edition_date: str | None = None
    tier_items: list[MastheadTierItem] = Field(min_length=1)
    aria_label: str = Field(default="Hauptnavigation", min_length=1)
    context_chip: MastheadChip | None = None
    user_chip_id: str | None = None
    """Optionaler Hydration-Slot. Gesetzt → ein Lade-Chip mit dieser id wird
    nach dem Kontext-Chip gerendert; eine App fuellt ihn client-seitig."""
    user_chip_label: str = "…"
    """Server-gerenderter Pre-Hydration-Text des Lade-Chips."""
