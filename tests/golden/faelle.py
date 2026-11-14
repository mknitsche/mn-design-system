"""Golden-Faelle fuer den Additivitaetsbeweis 0.24.0 (P8, Plan-Pruefung K1).

Jeder Fall ist ein Name und ein Aufruf OHNE neue Argumente. ``0_23_0.json`` haelt die Ausgabe,
die v0.23.0 dazu lieferte; ``test_alte_eingaben_rendern_wie_0_23_0`` je Komponente prueft
byte-gleich dagegen. ``erzeuge.py`` schreibt die Datei — NUR gegen einen Stand 0.23.0
laufen lassen (Tag ``v0.23.0``), nie gegen neueren Code, sonst beweist die Datei nichts.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from mn_design_system.components._patterns.contracts import (
    BackLinkInput,
    FooterInput,
    FooterLink,
    FooterSegment,
    KpiCardInput,
    MastheadChip,
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    PageHeaderInput,
    PfadZeileInput,
    SubNavInput,
    SubNavTab,
    WebTier,
)
from mn_design_system.components.web import (
    render_back_link_css,
    render_back_link_html,
    render_card_grid_css,
    render_datei_zeile_css,
    render_empty_state_css,
    render_font_face,
    render_footer_css,
    render_footer_html,
    render_foundation_css,
    render_initiale_css,
    render_kpi_card_css,
    render_kpi_card_html,
    render_masthead_css,
    render_masthead_html,
    render_page_header_css,
    render_page_header_html,
    render_pfad_zeile_css,
    render_pfad_zeile_html,
    render_sub_nav_css,
    render_sub_nav_html,
    render_sub_nav_js,
    render_tier_chip_css,
    render_zeitraum_leiste_css,
)

GOLDEN = Path(__file__).with_name("0_23_0.json")


def _sub_nav() -> SubNavInput:
    return SubNavInput(
        tier=WebTier.OBSERVATORIUM,
        tabs=[
            SubNavTab(label="Übersicht", href="/observatorium/", active=True),
            SubNavTab(label="Gesundheit", href="/observatorium/gesundheit/"),
            SubNavTab(label="Sport", href="/observatorium/sport/"),
        ],
    )


def _masthead(mit_chips: bool) -> MastheadInput:
    return MastheadInput(
        emblem=MastheadEmblem(src="/assets/logo.svg", alt="MKN", href="/start/"),
        wordmark="MKN 2nd Brain",
        edition_date="Samstag, 14. November" if mit_chips else None,
        tier_items=[
            MastheadTierItem(
                label="Start", href="/start/", tier=WebTier.START, active=True
            ),
            MastheadTierItem(label="Magazin", href="/magazin/", tier=WebTier.MAGAZIN),
        ],
        context_chip=MastheadChip(tier=WebTier.START, label="Start · GREEN")
        if mit_chips
        else None,
        user_chip_id="user-chip" if mit_chips else None,
    )


FAELLE: dict[str, Callable[[], str]] = {
    "pfad_zeile_html": lambda: render_pfad_zeile_html(
        PfadZeileInput(vorfahren=(("archiv", "/a/"), ("briefing", "/a/b/")))
    ),
    "pfad_zeile_css": render_pfad_zeile_css,
    "back_link_html": lambda: render_back_link_html(
        BackLinkInput(href="/start/", label="Start")
    ),
    "back_link_css": render_back_link_css,
    "sub_nav_html": lambda: render_sub_nav_html(_sub_nav()),
    "sub_nav_html_inline": lambda: render_sub_nav_html(_sub_nav(), inline_css=True),
    "sub_nav_css": render_sub_nav_css,
    "sub_nav_js": render_sub_nav_js,
    "masthead_html_voll": lambda: render_masthead_html(_masthead(True)),
    "masthead_html_schlicht": lambda: render_masthead_html(_masthead(False)),
    "masthead_html_inline": lambda: render_masthead_html(
        _masthead(True), inline_css=True
    ),
    "masthead_css": render_masthead_css,
    "font_face_praefix": lambda: render_font_face("/assets/fonts/"),
    "font_face_praefix_ohne_slash": lambda: render_font_face("/assets/fonts"),
    "font_face_leer": lambda: render_font_face(""),
    "foundation_css": render_foundation_css,
    "initiale_css": render_initiale_css,
    "kpi_card_html": lambda: render_kpi_card_html(
        KpiCardInput(label="Gewicht", value="80,1", caption="30 Tage")
    ),
    "kpi_card_css": render_kpi_card_css,
    "page_header_html": lambda: render_page_header_html(
        PageHeaderInput(title="Titel", lead="Lead")
    ),
    "page_header_css": render_page_header_css,
    "footer_html": lambda: render_footer_html(
        FooterInput(
            segments=[FooterSegment(text="MKN")],
            links=[FooterLink(label="Impressum", href="/impressum/")],
            version="0.23.0",
        )
    ),
    "footer_css": render_footer_css,
    "tier_chip_css": render_tier_chip_css,
    "card_grid_css": render_card_grid_css,
    "datei_zeile_css": render_datei_zeile_css,
    "empty_state_css": render_empty_state_css,
    "zeitraum_leiste_css": render_zeitraum_leiste_css,
}


def lade_golden() -> dict[str, str]:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def pruefe_praefix(praefix: str, golden: dict[str, str] | None = None) -> None:
    """Hilfe fuer die Tests: jeder Fall mit ``praefix`` stimmt byte-gleich mit der Datei."""
    golden = golden if golden is not None else lade_golden()
    namen = [n for n in FAELLE if n.startswith(praefix)]
    assert namen, f"kein Golden-Fall mit Praefix {praefix!r} (Untergrenze)"
    for name in namen:
        assert FAELLE[name]() == golden[name], f"{name} weicht von 0.23.0 ab"
