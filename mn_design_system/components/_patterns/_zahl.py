"""Deutsches Zahlenformat (0.18.0) — intern.

Der Verlauf-Chart (Beschreibung, Zielband) und die KPI-Karte (absolutes Delta) brauchen
dieselbe Schreibweise: Komma als Dezimal-, Punkt als Tausendertrenner, echtes
Minuszeichen. EINE Stelle statt zwei Kopien, die auseinanderlaufen.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

#: Minuszeichen U+2212 (kein Bindestrich): gleich breit wie das Plus, kein Trennstrich.
MINUS = "\u2212"

#: Geschuetztes Leerzeichen zwischen Zahl und Einheit (kein Umbruch dazwischen).
NBSP = "\u00a0"

_TAUSCH = str.maketrans(",.", ".,")


def zahl_de(wert: float, dezimalstellen: int) -> str:
    """Deutsche Zahl: Komma als Dezimal-, Punkt als Tausendertrenner."""
    return f"{wert:,.{dezimalstellen}f}".translate(_TAUSCH)


def zahl_de_kurz(wert: float, dezimalstellen: int) -> str:
    """Wie :func:`zahl_de`, aber ohne ueberfluessige Nullen hinter dem Komma.

    ``70.0`` wird „70", ``72.5`` bleibt „72,5". Die Nullen VOR dem Komma bleiben
    („100", „1.000"); ohne Dezimalstellen gibt es nichts zu kuerzen. Ein negativer Wert
    traegt das Minuszeichen U+2212 („−5"), nicht den Bindestrich — in „−5–5" waere ein
    Bindestrich vom Bis-Strich kaum zu unterscheiden; was auf null rundet, ist „0".
    """
    text = zahl_de(wert, dezimalstellen)
    if "," in text:
        text = text.rstrip("0").rstrip(",")
    if text == "-0":
        return "0"
    return text.replace("-", MINUS, 1)


def _gerundet(wert: float, dezimalstellen: int) -> Decimal:
    """Kaufmaennisch gerundet (halb aufwaerts, vom Betrag her) auf die Dezimalstellen.

    Aus der kuerzesten Dezimaldarstellung des Wertes (``repr``), nicht aus der
    Binaerzahl: 0,35 ist als Gleitkommazahl 0,34999…, wird aber als „0,35" gelesen.
    """
    return Decimal(repr(float(wert))).quantize(
        Decimal(1).scaleb(-dezimalstellen), rounding=ROUND_HALF_UP
    )


def rundet_auf_null(wert: float, dezimalstellen: int) -> bool:
    """Ist der Wert auf die Dezimalstellen gerundet null (auch -0,04 auf eine Stelle)?"""
    return _gerundet(wert, dezimalstellen) == 0


def delta_de(wert: float, dezimalstellen: int, einheit: str = "") -> str:
    """Absolutes Delta deutsch: „+1,2 kg" / „−1,2 kg" / „unverändert".

    Vorzeichen immer sichtbar (Plus, Minuszeichen U+2212); Tausenderpunkt ab 1.000;
    die Einheit folgt nach einem geschuetzten Leerzeichen. Rundet der Wert auf null,
    steht „unverändert" (weder „+0,0" noch „−0,0"), ohne Einheit.
    """
    q = _gerundet(wert, dezimalstellen)
    if q == 0:
        return "unverändert"
    zahl = format(abs(q), f",.{dezimalstellen}f").translate(_TAUSCH)
    text = f"{'+' if q > 0 else MINUS}{zahl}"
    return f"{text}{NBSP}{einheit}" if einheit else text
