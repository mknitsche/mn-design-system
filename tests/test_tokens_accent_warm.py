"""S239: accent.warm Token-Familie (Variante C').

KT-1's Wahl nach Live-PDF-Vergleich (3 Varianten A/B/C):
- accent.warm-strong = #b45309 (Copper-800, warm-erdig) - Section-Header
- accent.warm-amber  = #d97706 (Amber-600, Legacy-Alias) - hochkontrastive Badges
- accent.warm-soft   = #fef3c7 (Amber-100, helles Tint) - Hintergrund
- accent.warm-text   = #78350f (Amber-900, dunkel) - Schrift auf -soft

v0.5.4 KT-1 (S250 Claude Web Design, S251 macb-claude eingespielt):
strong wechselt von Amber-600 auf Copper-800 — warm-erdig statt orange,
harmoniert besser mit Indigo-Familie. Amber-600 bleibt als Legacy-Alias
unter accent.warm.amber erhalten (hochkontrastive Badge-Faelle).

Drift-Schutz: stellt sicher, dass spaetere Anpassungen die Sub-Tokens
nicht versehentlich aus der Tailwind-Amber/Copper-Skala (100/600/800/900)
heraus-laufen lassen — und dass die Werte nicht zufaellig in
status.warning/status.urgent kollidieren (semantische Trennung).
"""

from __future__ import annotations

from mn_design_system.tokens import get


def test_accent_warm_strong_ist_copper_800():
    """v0.5.4: strong = Copper-800 (#b45309), warm-erdig."""
    assert get("color.accent.warm.strong") == "#b45309"


def test_accent_warm_amber_ist_legacy_alias():
    """v0.5.4 Legacy-Alias: war bis v0.5.3 color.accent.warm.strong."""
    assert get("color.accent.warm.amber") == "#d97706"


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
    """Strong (#b45309) und Text (#78350f) muessen visuell deutlich
    voneinander abweichen — sonst geht die Hierarchie verloren."""
    strong = get("color.accent.warm.strong")
    text = get("color.accent.warm.text")
    # Erste Zwei Hex-Bytes liefern die "Helligkeits-Indikation" grob.
    # strong=b4 / text=78 - klare Differenz (180 vs 120 = 60).
    strong_lightness = int(strong[1:3], 16)  # 0xb4 = 180
    text_lightness = int(text[1:3], 16)  # 0x78 = 120
    assert strong_lightness - text_lightness > 50, (
        f"strong/text-Kontrast zu gering: {strong} vs {text}"
    )


def test_accent_warm_amber_und_strong_unterscheiden_sich():
    """v0.5.4: Legacy-Alias darf NICHT identisch mit neuem strong sein."""
    assert get("color.accent.warm.amber") != get("color.accent.warm.strong")
