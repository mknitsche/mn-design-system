"""0.25.0: Status-Flaechen-Tokens — Toenung, Rand, Schrift auf der Toenung, Statusschrift im Dunkeln.

Herkunft (Optik wie mkn-desk, claudeAI PR #1972; KT-1 2026-11-15: hell eine dezente Flaeche
plus farbiger Rand links, dunkel KEINE Flaeche, nur die Aussage-Schrift in der Statusfarbe):
Flaechen und Raender sind Aliase auf die Tokens, die mkn-desk direkt nutzt;
``text-muted-on-surface`` und ``color.dark.status-*`` sind die Toene, die mkn-desk per
``color-mix`` ableitet; ``success-/error-on-surface`` sind neu im DS (Delta der KPI-Karte).
Dieser Test beweist die Ableitung und dass jedes Paar WCAG AA erreicht (Schrift 4,5:1,
Rand als Grafik 3:1).
"""

from __future__ import annotations

import pytest

from mn_design_system.tokens import get

STUFEN = ("success", "warning", "error")


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _hex(c) -> str:
    return "#" + "".join(f"{round(v):02x}" for v in c)


def _mix(a: str, b: str, anteil_a: float) -> str:
    """sRGB-Mischung wie CSS ``color-mix(in srgb, a anteil_a, b)``."""
    return _hex(x * anteil_a + y * (1 - anteil_a) for x, y in zip(_rgb(a), _rgb(b)))


def _lum(h: str) -> float:
    def kanal(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (kanal(v) for v in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(a: str, b: str) -> float:
    hell, dunkel = sorted((_lum(a), _lum(b)), reverse=True)
    return (hell + 0.05) / (dunkel + 0.05)


# --- Werte = die Ableitung aus mkn-desk ----------------------------------------------------


def test_flaechen_sind_die_vorhandenen_toenungen():
    assert get("color.status.success-surface") == get("color.status.success-bg")
    assert get("color.status.warning-surface") == get("color.accent.warm.soft")
    assert get("color.status.error-surface") == get("color.status.error-bg")


def test_raender_sind_die_kraeftigen_statustoene():
    assert get("color.status.success-edge") == get("color.status.success")
    # status.warning (#f59e0b) laege auf der Toenung unter 3:1 — darum Copper-800
    assert get("color.status.warning-edge") == get("color.accent.warm.strong")
    assert get("color.status.error-edge") == get("color.status.error")


def test_schrift_auf_flaeche_ist_30_prozent_zur_textfarbe_gezogen():
    text = get("color.grey.700")
    assert get("color.status.text-muted-on-surface") == _mix(
        get("color.grey.500"), text, 0.70
    )
    assert get("color.status.success-on-surface") == _mix(
        get("color.status.success"), text, 0.70
    )
    assert get("color.status.error-on-surface").lower() == _mix(
        get("color.status.error"), text, 0.70
    )


def test_dunkle_statusschrift_ist_70_prozent_ton_auf_dunkler_textfarbe():
    d_text = get("color.dark.text")
    assert get("color.dark.status-success") == _mix(
        get("color.diagram.emerald.base"), d_text, 0.70
    )
    assert get("color.dark.status-warning") == _mix(
        get("color.accent.warm.amber"), d_text, 0.70
    )
    assert get("color.dark.status-error") == _mix(
        get("color.diagram.crimson.base"), d_text, 0.70
    )


def test_rand_breite():
    assert get("web.stroke.status-edge") == "4px"


# --- Kontrast WCAG AA ---------------------------------------------------------------------


def kontrast_tabelle() -> dict[str, float]:
    """Alle Lesbarkeits-Paare (auch Quelle der Tabelle im CHANGELOG)."""
    werte: dict[str, float] = {}
    for s in STUFEN:
        f = get(f"color.status.{s}-surface")
        for schrift in (
            "color.grey.700",
            "color.light.text",
            "color.light.h1",
            "color.status.text-muted-on-surface",
            "color.status.success-on-surface",
            "color.status.error-on-surface",
        ):
            werte[f"hell {s}: {schrift}"] = kontrast(get(schrift), f)
        werte[f"hell {s}: Rand (Grafik)"] = kontrast(get(f"color.status.{s}-edge"), f)
        werte[f"hell {s}: (roh) color.light.text-muted"] = kontrast(
            get("color.light.text-muted"), f
        )
        werte[f"hell {s}: (roh) color.status.success"] = kontrast(
            get("color.status.success"), f
        )
        werte[f"hell {s}: (roh) color.status.error"] = kontrast(
            get("color.status.error"), f
        )
        for flaeche in ("color.dark.surface", "color.dark.surface-subtle"):
            werte[f"dunkel {s}: auf {flaeche}"] = kontrast(
                get(f"color.dark.status-{s}"), get(flaeche)
            )
    return werte


def test_jedes_paar_erreicht_aa():
    zu_niedrig = {}
    for name, wert in kontrast_tabelle().items():
        if "(roh)" in name:
            continue
        grenze = 3.0 if "Grafik" in name else 4.5
        if wert < grenze:
            zu_niedrig[name] = round(wert, 2)
    assert not zu_niedrig, zu_niedrig


def test_untergrenze_ohne_anhebung_waere_es_zu_wenig():
    """Grund fuer die *-on-surface-Tokens: die rohen Toene liegen auf der Toenung unter 4,5."""
    roh = {k: v for k, v in kontrast_tabelle().items() if "(roh)" in k}
    assert any(v < 4.5 for k, v in roh.items() if "text-muted" in k)
    assert any(v < 4.5 for k, v in roh.items() if "status.error" in k)


@pytest.mark.parametrize("s", STUFEN)
def test_im_dunkeln_keine_flaeche_regel_ist_dokumentiert(s):
    """Die Regel „dunkel keine Flaeche“ steht am Token selbst (Kommentar), nicht nur im CHANGELOG."""
    import json
    from pathlib import Path

    farben = json.loads(
        (Path(__file__).parents[1] / "tokens" / "colors.json").read_text(
            encoding="utf-8"
        )
    )
    kommentar = farben["color"]["status"][f"{s}-surface"].get("comment", "")
    assert "dunkel" in kommentar.lower() and "keine" in kommentar.lower(), kommentar
