"""S239: accent.warm Token-Familie (Variante C').

KT-1's Wahl nach Live-PDF-Vergleich (3 Varianten A/B/C):
- accent.warm-strong = #d97706 (Amber-600, kupferig-edel) - Section-Header
- accent.warm-soft   = #fef3c7 (Amber-100, helles Tint) - Hintergrund
- accent.warm-text   = #78350f (Amber-900, dunkel) - Schrift auf -soft

Drift-Schutz: stellt sicher, dass spaetere Anpassungen die Sub-Tokens
nicht versehentlich aus der Tailwind-Amber-Skala (100/600/900) heraus-
laufen lassen — und dass die Werte nicht zufaellig in status.warning/
status.urgent kollidieren (semantische Trennung).
"""

from __future__ import annotations

from mn_design_system.tokens import get


def test_accent_warm_strong_ist_amber_600():
    assert get("color.accent.warm.strong") == "#d97706"


def test_accent_warm_soft_ist_amber_100():
    assert get("color.accent.warm.soft") == "#fef3c7"


def test_accent_warm_text_ist_amber_900():
    assert get("color.accent.warm.text") == "#78350f"


def test_accent_warm_distinct_von_status_warning():
    """accent.warm ist NICHT status.warning — semantische Trennung."""
    assert get("color.accent.warm.strong") != get("color.status.warning")


def test_accent_warm_distinct_von_status_urgent():
    """accent.warm ist NICHT status.urgent — semantische Trennung."""
    assert get("color.accent.warm.strong") != get("color.status.urgent")


def test_accent_warm_strong_und_text_haben_starken_kontrast():
    """Strong (#d97706) und Text (#78350f) muessen visuell deutlich
    voneinander abweichen — sonst geht die Hierarchie verloren."""
    strong = get("color.accent.warm.strong")
    text = get("color.accent.warm.text")
    # Erste Zwei Hex-Bytes liefern die "Helligkeits-Indikation" grob.
    # strong=d9 / text=78 - klare Differenz.
    strong_lightness = int(strong[1:3], 16)  # 0xd9 = 217
    text_lightness = int(text[1:3], 16)  # 0x78 = 120
    assert strong_lightness - text_lightness > 50, (
        f"strong/text-Kontrast zu gering: {strong} vs {text}"
    )
