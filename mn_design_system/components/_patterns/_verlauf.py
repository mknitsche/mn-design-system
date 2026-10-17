"""Gemeinsame Zeit- und Zahlen-Helfer des Verlauf-Charts (0.17.0).

Intern: der Vertrag (`contracts.py`, `beschreibung_text`) und der Renderer
(`components/web/verlauf_chart.py`) brauchen dieselbe Berliner Wanduhr und dieselbe
deutsche Zahlenschreibweise. EINE Stelle statt zwei Kopien, die auseinanderlaufen.
"""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

#: Zeitzone, in der ein `datetime` ohne Zone gelesen wird (mkn-desk.com ist ein
#: deutsches Produkt; ein naiver Zeitstempel ist Wanduhrzeit in Berlin).
VERLAUF_ZEITZONE = ZoneInfo("Europe/Berlin")


def zeit_als_berlin(t: date | datetime) -> date | datetime:
    """Ein `datetime` ohne Zone wird als Europe/Berlin gelesen (sonst unveraendert)."""
    if isinstance(t, datetime) and t.tzinfo is None:
        return t.replace(tzinfo=VERLAUF_ZEITZONE)
    return t


def berlin_wanduhr(t: date | datetime) -> datetime:
    """Zeitpunkt als Wanduhr in Berlin ohne Zone; ein `date` wird Mitternacht."""
    if not isinstance(t, datetime):
        return datetime.combine(t, time.min)
    if t.tzinfo is None:
        return t
    return t.astimezone(VERLAUF_ZEITZONE).replace(tzinfo=None)


def zahl_de(wert: float, dezimalstellen: int) -> str:
    """Deutsche Zahl: Komma als Dezimal-, Punkt als Tausendertrenner."""
    return f"{wert:,.{dezimalstellen}f}".translate(str.maketrans(",.", ".,"))


def datum_de(t: date | datetime) -> str:
    """`TT.MM.JJJJ` (Berliner Wanduhr)."""
    return berlin_wanduhr(t).strftime("%d.%m.%Y")
