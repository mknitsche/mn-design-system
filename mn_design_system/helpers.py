"""MN PKA Design-System — Token-Konsumtion-Helper (v0.4.4 / S248).

Stellt eine API zwischen Token-Speicher (mn_design_system.tokens.TOKENS) und
Konsumenten (ReportLab-Renderer, Web-CSS, LaTeX-Templates) zur Verfuegung.

Wurzel-Problem vor v0.4.4:
    TOKENS["space.4"] liefert "16px" als String. ReportLab-Renderer brauchen mm
    oder pt, nicht px-Strings. In claudeAI waren ~60 Stellen mit hardcoded
    "spaceBefore=4 * mm" weil der Konvertierungs-Helper fehlte.

Loesung v0.4.4:
    Helper-Funktionen `space_token`, `size_token`, `leading_token` mit
    `unit`-Parameter konvertieren explizit zwischen mm/pt/px/raw. Strict-Mode
    werft KeyError bei unbekanntem Token (Pattern 6 — kein stilles Fallback).

Konvention (DS-Decisions v03 §3):
    1 unit = 1mm = 2.835pt = 4px

Beispiel:
    >>> from mn_design_system import space_token, size_token
    >>> space_token("space.4", unit="mm")
    4.0
    >>> space_token("space.4", unit="pt")
    11.34
    >>> size_token("body", unit="pt")
    9.5
    >>> size_token("body", unit="px")
    13  # gerundet
"""

from __future__ import annotations

from typing import Literal

from .tokens import TOKENS

# ----------------------------------------------------------------------------
# Konvertierungs-Konvention (S248 KT-1-Setzung)
#
# Basis: mm. Konvertierung mit 1 unit = 1mm = 2.835pt = 4px.
# Krumme pt/px-Werte sind ReportLab/Browser-intern Float — kein Praxis-Problem.
# ----------------------------------------------------------------------------

MM_PER_INCH = 25.4
PT_PER_INCH = 72.0
MM_TO_PT = PT_PER_INCH / MM_PER_INCH  # = 2.83464567...
MM_TO_PX = 4.0  # Konvention: 1mm = 4px (1 design unit)
PX_TO_MM = 1.0 / MM_TO_PX  # = 0.25mm

Unit = Literal["mm", "pt", "px", "raw"]


# ----------------------------------------------------------------------------
# Wert-Parser
# ----------------------------------------------------------------------------

def _parse_value_to_mm(raw: str | int | float) -> float:
    """Akzeptiert 'Npx', 'Nmm', 'Npt', oder Integer/Float (= dimensionslos units)."""
    if isinstance(raw, (int, float)):
        return float(raw)  # dimensionslos = mm

    s = str(raw).strip().lower()
    if s.endswith("mm"):
        return float(s[:-2])
    if s.endswith("pt"):
        return float(s[:-2]) / MM_TO_PT
    if s.endswith("px"):
        return float(s[:-2]) * PX_TO_MM
    if s.endswith("rem"):
        # rem ist Web-Skalierung, hier nicht sinnvoll konvertierbar
        raise ValueError(f"Cannot convert 'rem' value to mm: {raw!r}")
    # Default: nackte Zahl als mm
    try:
        return float(s)
    except ValueError as exc:
        raise ValueError(f"Unknown unit suffix in {raw!r}") from exc


def _convert_mm(value_mm: float, unit: Unit) -> float | int:
    """Konvertiert mm-Wert in Ziel-Einheit."""
    if unit == "mm":
        return round(value_mm, 4)
    if unit == "pt":
        return round(value_mm * MM_TO_PT, 4)
    if unit == "px":
        return round(value_mm * MM_TO_PX, 4)
    if unit == "raw":
        return value_mm
    raise ValueError(f"Unknown unit {unit!r}, must be one of mm/pt/px/raw")


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------

def space_token(key: str, unit: Unit = "mm") -> float | int:
    """Spacing-Token in gewuenschter Einheit.

    Args:
        key: Token-Schluessel (z.B. "space.4", "space.semantic.default", "space.indent.bullet")
        unit: Ziel-Einheit. mm fuer Print/PDF, pt fuer ReportLab, px fuer Web/CSS, raw dimensionslos.

    Returns:
        Numerischer Wert in gewaehlter Einheit.

    Raises:
        KeyError: Token nicht in TOKENS (Strict-Mode, kein Fallback).
        ValueError: Wert-Format nicht parsebar (z.B. rem).

    Examples:
        >>> space_token("space.4", unit="mm")
        4.0
        >>> space_token("space.4", unit="pt")
        11.3386
        >>> space_token("space.semantic.default", unit="mm")
        3.0
        >>> space_token("space.indent.bullet", unit="mm")
        3.0
    """
    if key not in TOKENS:
        raise KeyError(f"Unknown spacing token: {key!r} (available: {[k for k in TOKENS if k.startswith('space.')][:10]} ...)")
    raw = TOKENS[key]
    value_mm = _parse_value_to_mm(raw)
    return _convert_mm(value_mm, unit)


def size_token(key: str, unit: Unit = "pt") -> float | int:
    """Schriftgroessen-Token.

    Args:
        key: Token-Schluessel ohne 'font.size.' Praefix erlaubt (z.B. "body" oder "font.size.body").
        unit: Ziel-Einheit. pt ist Default fuer ReportLab.

    Returns:
        Schriftgroesse in gewaehlter Einheit.

    Examples:
        >>> size_token("body")
        9.5
        >>> size_token("font.size.body")
        9.5
        >>> size_token("footer-page")
        8.0
        >>> size_token("title-page")
        22.0
    """
    full_key = key if key.startswith("font.size.") else f"font.size.{key}"
    if full_key not in TOKENS:
        avail = [k.replace("font.size.", "") for k in TOKENS if k.startswith("font.size.")]
        raise KeyError(f"Unknown size token: {key!r} (available: {avail})")
    raw = TOKENS[full_key]
    # Schriftgroessen sind in pt gespeichert, ggf. konvertieren
    if str(raw).endswith("pt"):
        value_pt = float(str(raw)[:-2])
    elif str(raw).endswith("px"):
        # px -> pt via Konvention 4px = 3pt (96 DPI), aber das ist Web-Konvention
        # Schriftgroessen sind aber pt-nativ; falls px, dann via mm
        value_pt = float(str(raw)[:-2]) * PX_TO_MM * MM_TO_PT
    else:
        value_pt = float(raw)

    if unit == "pt":
        return round(value_pt, 4)
    if unit == "mm":
        return round(value_pt / MM_TO_PT, 4)
    if unit == "px":
        return round(value_pt * (4.0 / 3.0), 4)  # Web-Konvention 1pt = 4/3 px (96 DPI)
    if unit == "raw":
        return value_pt
    raise ValueError(f"Unknown unit {unit!r}")


def leading_token(key: str, unit: Unit = "pt") -> float | int:
    """Leading-Token (Zeilenabstand).

    Args:
        key: Token-Schluessel ohne 'font.leading.' Praefix erlaubt.
        unit: Ziel-Einheit. pt ist Default fuer ReportLab.

    Examples:
        >>> leading_token("body")
        13.5
        >>> leading_token("footer-page")
        10.0
    """
    full_key = key if key.startswith("font.leading.") else f"font.leading.{key}"
    if full_key not in TOKENS:
        avail = [k.replace("font.leading.", "") for k in TOKENS if k.startswith("font.leading.")]
        raise KeyError(f"Unknown leading token: {key!r} (available: {avail})")
    raw = TOKENS[full_key]
    if str(raw).endswith("pt"):
        value_pt = float(str(raw)[:-2])
    else:
        value_pt = float(raw)

    if unit == "pt":
        return round(value_pt, 4)
    if unit == "mm":
        return round(value_pt / MM_TO_PT, 4)
    if unit == "px":
        return round(value_pt * (4.0 / 3.0), 4)
    if unit == "raw":
        return value_pt
    raise ValueError(f"Unknown unit {unit!r}")


def color_token(key: str) -> str:
    """Farb-Token als Hex-String.

    Args:
        key: Token-Schluessel (z.B. "color.severity.high", "color.indigo.900").

    Returns:
        Hex-Wert als String, z.B. "#dc2626".

    Examples:
        >>> color_token("color.severity.high")
        '#dc2626'
        >>> color_token("color.severity.medium")
        '#a16207'
    """
    if key not in TOKENS:
        avail = [k for k in TOKENS if k.startswith("color.")]
        raise KeyError(f"Unknown color token: {key!r} (available: {len(avail)} color tokens)")
    return TOKENS[key]


def font_family(key: str) -> str:
    """Font-Familie-Token.

    Args:
        key: Token-Schluessel ohne 'font.family.' Praefix erlaubt.

    Returns:
        Font-Familien-Name (z.B. "Geist", "STIXTwoText").

    Examples:
        >>> font_family("sans")
        'Geist'
        >>> font_family("fallback-greek")
        'STIXTwoText'
        >>> font_family("table-data")
        'JetBrainsMono'
    """
    full_key = key if key.startswith("font.family.") else f"font.family.{key}"
    if full_key not in TOKENS:
        avail = [k.replace("font.family.", "") for k in TOKENS if k.startswith("font.family.")]
        raise KeyError(f"Unknown font family token: {key!r} (available: {avail})")
    return TOKENS[full_key]


# ----------------------------------------------------------------------------
# Greek-Letter / Math-Symbol Fallback (S248 — Sigma-Glyph-Bug)
# ----------------------------------------------------------------------------

# Unicode-Bereiche fuer Greek + Math-Symbols, die Geist nicht enthaelt.
# Greek and Coptic: U+0370 - U+03FF
# Greek Extended:   U+1F00 - U+1FFF
# Math Operators:   U+2200 - U+22FF
# Math Misc:        U+27C0 - U+27EF
_GREEK_RANGES = [
    (0x0370, 0x03FF),
    (0x1F00, 0x1FFF),
    (0x2200, 0x22FF),
    (0x27C0, 0x27EF),
]


def _is_greek_or_math(char: str) -> bool:
    """True wenn Zeichen aus Greek/Math-Unicode-Bereich kommt."""
    if not char:
        return False
    cp = ord(char)
    return any(lo <= cp <= hi for lo, hi in _GREEK_RANGES)


def font_with_fallback(text: str, default_font: str | None = None) -> str:
    """Wrappt Greek/Math-Letters in <font name="STIXTwoText">...</font>-Tags.

    Fuer ReportLab Paragraph-Konsumenten: Geist enthaelt keine Greek-Letters
    (sigma, alpha, beta, gamma, delta, ...), Math-Operatoren etc. Wuerde im
    PDF als Box-Glyph rendern. Diese Funktion umrahmt einzelne Greek-Chars
    (oder zusammenhaengende Sequenzen) mit dem STIXTwoText-Fallback.

    Args:
        text: Eingabe-Text mit ggf. Greek-Letters.
        default_font: Default-Font fuer Nicht-Greek-Bereiche. None = ReportLab
                      nutzt die Style-Default (z.B. Geist).

    Returns:
        ReportLab-Inline-Markup-String mit <font>-Wrappern um Greek-Bereiche.

    Examples:
        >>> font_with_fallback("Vol-Spike +1,8 sigma")
        'Vol-Spike +1,8 sigma'
        >>> font_with_fallback("Vol-Spike +1,8 σ über Median")
        'Vol-Spike +1,8 <font name="STIXTwoText">σ</font> über Median'
        >>> font_with_fallback("α/β/γ Vergleich")
        '<font name="STIXTwoText">α/β/γ</font> Vergleich'
    """
    if not text:
        return text

    fallback = font_family("fallback-greek")
    out = []
    in_greek = False
    buf = []

    for char in text:
        if _is_greek_or_math(char) or (in_greek and char in "/-_, "):
            # Innerhalb Greek-Sequenz auch Trennzeichen mitnehmen ("α/β/γ")
            # aber NUR wenn wir bereits in einer Greek-Sequenz sind
            if not _is_greek_or_math(char):
                # Whitespace/Trenner nur sammeln wenn bereits im Greek-Block
                if in_greek:
                    buf.append(char)
                    continue
                else:
                    out.append(char)
                    continue
            if not in_greek:
                in_greek = True
                buf = [char]
            else:
                buf.append(char)
        else:
            if in_greek:
                # Greek-Sequenz beenden, Trailing-Trenner aus buf entfernen
                while buf and buf[-1] in "/-_, ":
                    char = buf.pop() + char
                out.append(f'<font name="{fallback}">{"".join(buf)}</font>')
                buf = []
                in_greek = False
            out.append(char)

    if in_greek and buf:
        out.append(f'<font name="{fallback}">{"".join(buf)}</font>')

    return "".join(out)


# ----------------------------------------------------------------------------
# Convenience-Aliase (kompatibel zu existierenden claudeAI-Konsumenten)
# ----------------------------------------------------------------------------

def token(key: str, default=None):
    """Generischer Token-Lookup (mit Default). Behaelt v0.4.3-API."""
    return TOKENS.get(key, default)


__all__ = [
    "space_token",
    "size_token",
    "leading_token",
    "color_token",
    "font_family",
    "font_with_fallback",
    "token",
    "TOKENS",
    "MM_TO_PT",
    "MM_TO_PX",
]
