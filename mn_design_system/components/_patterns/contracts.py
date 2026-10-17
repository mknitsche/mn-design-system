"""Pydantic-Contracts fuer Komponenten-Inputs (Welle B v0.2.0).

Maschinen-lesbare API-Definitionen. Renderer-Implementierungen (pdf/, web/, latex/)
muessen diese als Eingabe akzeptieren — Mismatch wird beim Konstruktor sichtbar.

Begruendung (Gemini-Befund 5 v1.1->v1.2): Markdown-Specs allein sind menschlich
lesbar, aber nicht maschinell ueberpruefbar. Pydantic erzwingt Typ-Konsistenz
zwischen Spec und Implementation.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from mn_design_system.components._patterns._verlauf import (
    berlin_wanduhr,
    datum_de,
    zeit_als_berlin,
)
from mn_design_system.components._patterns._zahl import (
    delta_de,
    rundet_auf_null,
    zahl_de,
)

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


class KpiWertung(str, Enum):
    """Bewertung einer Bewegung: war sie gut, schlecht oder ist sie nicht zu werten.

    Folgt aus der Bewegung (``KpiTrendDirection``) und der Polaritaet
    (``KpiCardInput.richtung``): beim Gewicht ist ein Rueckgang GUT, bei den Schritten
    ein Anstieg.
    """

    GUT = "gut"
    SCHLECHT = "schlecht"
    NEUTRAL = "neutral"


class KpiCardInput(BaseModel):
    """API-Contract fuer build_kpi_card().

    label: Kicker-Text (z.B. "DAX")
    value: Hauptwert formatiert (z.B. "22.450")
    change_pct: optional, prozentuale Veraenderung (positiv/negativ/null)
    sparkline_values: optional Zeitreihe fuer kleine Trend-Linie
    caption: optional Untertitel-Text (z.B. "30 Tage")

    Seit 0.17.1 (alle optional, ohne sie aendert sich nichts):
    richtung: Polaritaet — welche Bewegung ist GUT? "hoeher" (Default: Anstieg gut,
        gruen), "niedriger" (Rueckgang gut, z.B. Gewicht, Ruhepuls) oder "neutral"
        (keine Wertung, immer gedaempft).
    delta_wert: absolutes Delta statt Prozent (z.B. -1.2 fuer "−1,2 kg"); deutsch
        formatiert. Zugleich mit change_pct nicht erlaubt (Mehrdeutigkeit).
    delta_einheit: Einheit hinter dem Delta ("kg"); nur mit delta_wert.
    dezimalstellen: Nachkommastellen des Deltas (0..6, Default 1). Rundet das Delta
        damit auf null, steht "unveraendert" und die Bewegung gilt als neutral.
    """

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1)
    value: str = Field(min_length=1)
    change_pct: float | None = None
    sparkline_values: list[float] | None = None
    caption: str | None = None
    richtung: Literal["hoeher", "niedriger", "neutral"] = "hoeher"
    delta_wert: float | None = Field(default=None, allow_inf_nan=False)
    delta_einheit: str = ""
    dezimalstellen: int = Field(default=1, ge=0, le=6)

    @model_validator(mode="after")
    def _delta_eindeutig(self) -> KpiCardInput:
        if self.delta_wert is not None and self.change_pct is not None:
            raise ValueError(
                "change_pct und delta_wert zugleich sind mehrdeutig: die Karte zeigt "
                "genau EIN Delta (Prozent oder absolut)"
            )
        if self.delta_einheit and self.delta_wert is None:
            raise ValueError("delta_einheit braucht delta_wert")
        return self

    def trend_direction(self) -> KpiTrendDirection:
        """Abgeleiteter Trend aus change_pct oder delta_wert.

        v0.4.1 (S239 B5): Schwellwert von 0.01 auf 0.5 hochgezogen — KT-1
        Briefing-Befund 30.04.: kleine Bewegungen (<0.5%) sollen nicht
        rot/gruen markiert werden, sondern neutral (grau, color.viz.muted).

        v0.17.1: bei gesetztem ``delta_wert`` entscheidet das Vorzeichen; ein Delta,
        das auf ``dezimalstellen`` gerundet null ist, gilt als neutral (keine
        Prozent-Schwelle: sie gehoert dem Prozentwert).
        """
        if self.delta_wert is not None:
            if rundet_auf_null(self.delta_wert, self.dezimalstellen):
                return KpiTrendDirection.NEUTRAL
            return (
                KpiTrendDirection.UP if self.delta_wert > 0 else KpiTrendDirection.DOWN
            )
        if self.change_pct is None or abs(self.change_pct) < 0.5:
            return KpiTrendDirection.NEUTRAL
        return KpiTrendDirection.UP if self.change_pct > 0 else KpiTrendDirection.DOWN

    def wertung(self) -> KpiWertung:
        """Bewegung und Polaritaet zusammen: war es gut, schlecht oder ungewertet."""
        richtung = self.trend_direction()
        if richtung == KpiTrendDirection.NEUTRAL or self.richtung == "neutral":
            return KpiWertung.NEUTRAL
        gut_bei = (
            KpiTrendDirection.UP
            if self.richtung == "hoeher"
            else KpiTrendDirection.DOWN
        )
        return KpiWertung.GUT if richtung == gut_bei else KpiWertung.SCHLECHT

    def delta_text(self) -> str | None:
        """Deutsch formatiertes absolutes Delta ("−1,2 kg"), ohne Delta ``None``."""
        if self.delta_wert is None:
            return None
        return delta_de(self.delta_wert, self.dezimalstellen, self.delta_einheit)


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
    """Die sechs Web-Tier von mkn-desk.com. Mappt auf color.tier.<tier>.*."""

    BIBLIOTHEK = "bibliothek"
    ATELIER = "atelier"
    KABINETT = "kabinett"
    START = "start"
    OBSERVATORIUM = "observatorium"
    MAGAZIN = "magazin"


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


class ZeitraumOption(BaseModel):
    """Eine Option der Zeitraum-Leiste (0.17.1).

    label: sichtbarer Text ("30 Tage").
    href: Adresse der Option ("?tage=30") — die Leiste besteht aus Links.
    active: True = die aktuell gewaehlte Option (aria-current="page").
    """

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1)
    href: str = Field(min_length=1)
    active: bool = False


class ZeitraumLeisteInput(BaseModel):
    """Zeitraum-Leiste (0.17.1): Segment-Leiste aus Links, z.B. fuer ``?tage=30|90|365``.

    optionen: 2..6 Optionen (eine einzelne waere keine Auswahl). Hoechstens eine ist
              aktiv; keine aktive Option ist erlaubt (der Konsument kennt dann den
              Wert der Adresse nicht, z.B. ``?tage=7``).
    aria_label: Landmark-Label des <nav> (WCAG 2.4.1), Default "Zeitraum".
    """

    model_config = {"extra": "forbid", "frozen": True}

    optionen: list[ZeitraumOption] = Field(min_length=2, max_length=6)
    aria_label: str = Field(default="Zeitraum", min_length=1)

    @model_validator(mode="after")
    def _hoechstens_eine_aktiv(self) -> ZeitraumLeisteInput:
        if sum(o.active for o in self.optionen) > 1:
            raise ValueError("hoechstens eine Option darf aktiv sein")
        return self


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


# ---------------------------------------------------------------------------
# Verlauf-Chart (0.17.0) — Zeitreihen-Diagramm auf Apache ECharts
# ---------------------------------------------------------------------------


class VerlaufPunkt(BaseModel):
    """Ein Messpunkt: Zeitpunkt (Tag oder Zeitstempel) und Wert.

    t: `date` fuer Tageswerte, `datetime` fuer Zeitpunkt-Werte. Ein `datetime`
       ohne Zeitzone wird als Europe/Berlin gelesen.
    wert: endliche Zahl (NaN/Infinity sind in JSON nicht darstellbar).
    """

    model_config = {"extra": "forbid", "frozen": True}

    t: date | datetime
    wert: float = Field(allow_inf_nan=False)

    @field_validator("t")
    @classmethod
    def _t_berlin(cls, t: date | datetime) -> date | datetime:
        return zeit_als_berlin(t)


class VerlaufReihe(BaseModel):
    """Eine Linie im Diagramm.

    label: Name in Legende und Tooltip (1..40 Zeichen).
    punkte: Messpunkte; darf leer sein (die Achse steht auch ohne Daten).
    art: "messung" = durchgezogene Linie, "gleitend" = gestrichelte Glaettung.
    """

    model_config = {"extra": "forbid", "frozen": True}

    label: str = Field(min_length=1, max_length=40)
    punkte: list[VerlaufPunkt]
    art: Literal["messung", "gleitend"] = "messung"


class VerlaufMarkierung(BaseModel):
    """Senkrechte Marke (Ereignis) im Diagramm: Zeitpunkt und kurze Beschriftung."""

    model_config = {"extra": "forbid", "frozen": True}

    t: date | datetime
    label: str = Field(min_length=1, max_length=30)

    @field_validator("t")
    @classmethod
    def _t_berlin(cls, t: date | datetime) -> date | datetime:
        return zeit_als_berlin(t)


class VerlaufChartInput(BaseModel):
    """API-Contract fuer render_verlauf_chart_html() / verlauf_chart_option().

    titel / einheit: Ueberschrift (1..80) und Einheit der Werteachse (0..16).
    reihen: 1..4 Linien; Punkte ausserhalb von `von`..`bis` werden nicht gezeichnet.
    von / bis: sichtbares Zeitfenster (ganze Tage, `bis` einschliesslich); die
       Zeitachse steht auch ohne Punkte. Es gilt von < bis.
    zielband_min / zielband_max: optionales Band; beide oder keins, min <= max.
    markierungen: hoechstens 12 senkrechte Ereignis-Marken.
    dezimalstellen: Nachkommastellen in Achse und Tooltip (0..3).
    hoehe: Flaechenhoehe in px, nur feste Stufen (das CSS kennt je Stufe eine
       Klasse; ein `style=`-Attribut gibt es bewusst nie).
    beschreibung: aria-label der Flaeche; ohne Angabe liefert
       `beschreibung_text()` einen Text aus Titel, Einheit, Letztstand, Zeitraum.
    """

    model_config = {"extra": "forbid", "frozen": True}

    titel: str = Field(min_length=1, max_length=80)
    einheit: str = Field(max_length=16)
    reihen: list[VerlaufReihe] = Field(min_length=1, max_length=4)
    von: date
    bis: date
    zielband_min: float | None = Field(default=None, allow_inf_nan=False)
    zielband_max: float | None = Field(default=None, allow_inf_nan=False)
    markierungen: list[VerlaufMarkierung] = Field(default_factory=list, max_length=12)
    dezimalstellen: int = Field(default=1, ge=0, le=3)
    hoehe: Literal[180, 220, 260, 320, 400, 600] = 260
    beschreibung: str | None = None

    @model_validator(mode="after")
    def _fenster_und_zielband(self) -> VerlaufChartInput:
        if self.von >= self.bis:
            raise ValueError("von muss vor bis liegen")
        if (self.zielband_min is None) != (self.zielband_max is None):
            raise ValueError("Zielband braucht Minimum und Maximum (beide oder keins)")
        if self.zielband_min is not None and self.zielband_min > self.zielband_max:
            raise ValueError("Zielband: Minimum darf das Maximum nicht uebersteigen")
        return self

    def beschreibung_text(self) -> str:
        """aria-label: die explizite `beschreibung`, sonst ein Satz aus den Daten.

        Der Default nennt Titel, Einheit, den juengsten Punkt der ERSTEN Reihe im
        Fenster (mit Datum) und den Zeitraum — ein Screenreader-Nutzer erfaehrt
        so den Stand, ohne das Diagramm zu sehen.
        """
        if self.beschreibung is not None:
            return self.beschreibung
        kopf = f"{self.titel} ({self.einheit})" if self.einheit else self.titel
        zeitraum = f"{datum_de(self.von)} bis {datum_de(self.bis)}"
        im_fenster = [
            p
            for p in self.reihen[0].punkte
            if self.von <= berlin_wanduhr(p.t).date() <= self.bis
        ]
        if not im_fenster:
            return f"{kopf}: keine Werte im Zeitraum {zeitraum}."
        letzter = max(im_fenster, key=lambda p: berlin_wanduhr(p.t))
        wert = zahl_de(letzter.wert, self.dezimalstellen)
        mit_einheit = f"{wert} {self.einheit}" if self.einheit else wert
        return (
            f"{kopf}: zuletzt {mit_einheit} am {datum_de(letzter.t)}, "
            f"Zeitraum {zeitraum}."
        )
