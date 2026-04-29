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
        """Abgeleiteter Trend aus change_pct."""
        if self.change_pct is None or abs(self.change_pct) < 0.01:
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
