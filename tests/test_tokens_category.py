"""color.category.* — To-Do-Prioritaets-Farben, Option-B Temperatur-Skala (v0.12.0).

KT-1 S260, Welle 3. Vier Prioritaets-Stufen ueber Farb-TEMPERATUR statt vier
unverbundener Material-Toene: Sofort=warm-rot, Demnaechst=warm-amber,
Klaeren=kuehl-indigo, Irgendwann=neutral-grau. Plus eine einheitliche
Checkbox-Farbe (Action-Indigo).

Ersetzt die 11 Material-Design-Adhoc-Tokens aus v0.11.0. Alle Werte sind
Style-Dictionary-Referenzen auf bestehende Marken-Tokens — einzige Ausnahme
prio-sofort-header-text (red-700, kein bestehender Token).

Drift-Schutz:
- alle 11 Tokens vorhanden + valides Hex
- die prio-*-bg/text-Werte sind tatsaechlich die referenzierten Marken-Tokens
- WCAG: prio-*-header-text auf zugehoerigem bg >=4.5:1 (Kleintext)
- die alten v0.11.0-Material-Tokens sind weg
"""

from __future__ import annotations

import re

from mn_design_system.tokens import get

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

_ALL_KEYS = [
    "prio-sofort-bg",
    "prio-sofort-text",
    "prio-sofort-header-text",
    "prio-demnaechst-bg",
    "prio-demnaechst-text",
    "prio-klaeren-bg",
    "prio-klaeren-text",
    "prio-irgendwann-bg",
    "prio-irgendwann-text",
    "prio-irgendwann-header-text",
    "checkbox",
]


def _rl(hex_str: str) -> float:
    h = hex_str.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))

    def lin(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _ratio(a: str, b: str) -> float:
    la, lb = _rl(a), _rl(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def test_alle_11_category_tokens_vorhanden():
    for key in _ALL_KEYS:
        assert get(f"color.category.{key}") is not None, f"Token fehlt: {key}"


def test_alle_category_tokens_sind_valides_hex():
    for key in _ALL_KEYS:
        val = get(f"color.category.{key}")
        assert _HEX.match(val), f"color.category.{key} kein Hex: {val}"


def test_prio_referenzen_zeigen_auf_marken_tokens():
    """Die bg/text-Werte sind Referenzen — muessen die Marken-Tokens treffen."""
    assert get("color.category.prio-sofort-bg") == get("color.status.error-bg")
    assert get("color.category.prio-sofort-text") == get("color.severity.high")
    assert get("color.category.prio-demnaechst-bg") == get("color.accent.warm.soft")
    assert get("color.category.prio-demnaechst-text") == get("color.accent.warm.text")
    assert get("color.category.prio-klaeren-bg") == get("color.indigo.100")
    assert get("color.category.prio-klaeren-text") == get("color.indigo.700")
    assert get("color.category.prio-irgendwann-bg") == get("color.grey.50")
    assert get("color.category.prio-irgendwann-text") == get("color.grey.500")
    assert get("color.category.prio-irgendwann-header-text") == get("color.grey.700")


def test_checkbox_ist_action_indigo():
    """Einheitliche Checkbox-Farbe = indigo-600 (Action)."""
    assert get("color.category.checkbox") == get("color.indigo.600")


def test_wcag_sofort_header_text():
    """prio-sofort-header-text >=4.5:1 auf prio-sofort-bg (Kleintext-AA)."""
    fg = get("color.category.prio-sofort-header-text")
    bg = get("color.category.prio-sofort-bg")
    r = _ratio(fg, bg)
    assert r >= 4.5, f"prio-sofort-header-text auf bg nur {r:.2f}:1 (<4.5:1)"


def test_wcag_irgendwann_header_text():
    """prio-irgendwann-header-text >=4.5:1 auf prio-irgendwann-bg."""
    fg = get("color.category.prio-irgendwann-header-text")
    bg = get("color.category.prio-irgendwann-bg")
    r = _ratio(fg, bg)
    assert r >= 4.5, f"prio-irgendwann-header-text auf bg nur {r:.2f}:1 (<4.5:1)"


def test_wcag_demnaechst_und_klaeren_text():
    """Demnaechst + Klaeren tragen Marken-Text-Tokens mit ausreichend Kontrast."""
    for prio in ["demnaechst", "klaeren"]:
        fg = get(f"color.category.prio-{prio}-text")
        bg = get(f"color.category.prio-{prio}-bg")
        r = _ratio(fg, bg)
        assert r >= 4.5, f"prio-{prio}-text auf bg nur {r:.2f}:1 (<4.5:1)"


def test_alte_v0_11_material_tokens_entfernt():
    """v0.11.0-Adhoc-Tokens (Material-Design-Literale) sind retired."""
    for old in [
        "yellow",
        "red-bg",
        "red-cb",
        "yellow-bg",
        "yellow-cb",
        "blue-bg",
        "blue-text",
        "blue-cb",
        "gray-text",
        "gray-cb",
        "green-cb",
    ]:
        assert get(f"color.category.{old}") is None, (
            f"v0.11.0-Adhoc-Token nicht entfernt: color.category.{old}"
        )


def test_architecture_familie_entfernt():
    """color.architecture.* ist in v0.12.0 retired (zugunsten color.diagram.*)."""
    for old in [
        "workflow",
        "workflow-light",
        "integration",
        "integration-light",
        "data",
        "data-light",
    ]:
        assert get(f"color.architecture.{old}") is None, (
            f"color.architecture.{old} nicht entfernt"
        )
