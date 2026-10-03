"""Responsive-Verhalten auf schmalen Viewports (0.14.1, Handy-Breite 390 px).

Drei Komponenten liefen auf dem Handy ueber den Bildschirm und erzeugten
horizontalen Seiten-Scroll: die Kontext-Chips des Masthead, die Tab-Zeile der
Sub-Nav und das Card-Grid mit fester Spaltenzahl.

Zwei Ebenen, weil jede allein luegt:

- CSS-Struktur (immer): die Regeln stehen in der richtigen Media-Query, die
  Desktop-Regeln sind unveraendert, die Breakpoints kommen aus den Tokens.
  Das beweist die Schreibweise, nicht die Wirkung.
- Browser-Wirkung (nur mit Playwright + Chromium; sonst sichtbar uebersprungen,
  nie still gruen): eine echte Seite wird bei 1440/768/390 px gemessen.
  Das beweist die Wirkung, ersetzt aber nicht die schnellen Struktur-Tests.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mn_design_system.components._patterns.contracts import (
    CardGridInput,
    ContentCardInput,
    MastheadChip,
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    SubNavInput,
    SubNavTab,
    WebTier,
)
from mn_design_system.components.web.content_card import (
    render_card_grid_css,
    render_card_grid_html,
    render_content_card_css,
)
from mn_design_system.components.web.foundation import (
    media_max_width_below,
    render_foundation_css,
)
from mn_design_system.components.web.masthead import (
    render_masthead_css,
    render_masthead_html,
)
from mn_design_system.components.web.sub_nav import (
    render_sub_nav_css,
    render_sub_nav_html,
)
from mn_design_system.tokens import get

# --------------------------------------------------------------------------
# CSS-Hilfen — bewusst klein: Media-Bloecke und Regel-Rumpfe auslesen.
# --------------------------------------------------------------------------


def _split_media(css: str, query: str) -> tuple[str, list[str]]:
    """Zerlegt css in (Text ausserhalb jeder `@media <query>`, [Block-Inhalte])."""
    marker = f"@media ({query})"
    outside: list[str] = []
    blocks: list[str] = []
    pos = 0
    while True:
        start = css.find(marker, pos)
        if start == -1:
            outside.append(css[pos:])
            break
        outside.append(css[pos:start])
        open_brace = css.index("{", start)
        depth, i = 0, open_brace
        while True:
            depth += css[i] == "{"
            depth -= css[i] == "}"
            if depth == 0:
                break
            i += 1
        blocks.append(css[open_brace + 1 : i])
        pos = i + 1
    return "".join(outside), blocks


def _rule(css: str, selector: str) -> str:
    """Deklarationen der Regel mit GENAU diesem Selektor ('' wenn es keine gibt)."""
    m = re.search(r"(?:^|})\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return m.group(1) if m else ""


def _below(token: str) -> str:
    """Erwartete Media-Query-Bedingung 'knapp unter dem Breakpoint <token>'."""
    px = float(get(token).removesuffix("px"))
    return f"max-width: {px - 0.02:g}px"


# --------------------------------------------------------------------------
# Hilfsfunktion in der Foundation
# --------------------------------------------------------------------------


class TestMediaMaxWidthBelow:
    def test_is_strictly_below_the_breakpoint(self):
        assert media_max_width_below("web.layout.bp-mobile") == "max-width: 639.98px"
        assert media_max_width_below("web.layout.bp-tablet") == "max-width: 1023.98px"

    def test_foundation_css_itself_is_unchanged(self):
        """Die Foundation behaelt ihre inklusiven Queries (bestehender Vertrag)."""
        css = render_foundation_css()
        assert "@media (max-width: 640px)" in css
        assert "@media (max-width: 1024px)" in css


# --------------------------------------------------------------------------
# Masthead
# --------------------------------------------------------------------------


class TestMastheadWrapsContextChips:
    def test_tiers_row_may_wrap(self):
        body = _rule(render_masthead_css(), ".mn-masthead__tiers-inner")
        assert "flex-wrap: wrap" in body

    def test_context_chips_may_wrap(self):
        body = _rule(render_masthead_css(), ".mn-masthead__context")
        assert "flex-wrap: wrap" in body

    def test_pills_stay_one_row(self):
        body = _rule(render_masthead_css(), ".mn-masthead__pills")
        assert "flex-wrap: wrap" not in body

    def test_desktop_layout_declarations_unchanged(self):
        css = render_masthead_css()
        tiers = _rule(css, ".mn-masthead__tiers-inner")
        for decl in (
            "display: flex",
            "align-items: center",
            "justify-content: space-between",
            "gap: var(--space-3, 12px)",
            "padding-block: var(--space-2, 8px)",
        ):
            assert decl in tiers
        context = _rule(css, ".mn-masthead__context")
        for decl in (
            "display: flex",
            "align-items: center",
            "gap: var(--space-2, 8px)",
        ):
            assert decl in context

    def test_masthead_needs_no_media_query(self):
        """Umbrechen statt Breakpoint: das Masthead bleibt breakpoint-frei."""
        assert "@media" not in render_masthead_css()


# --------------------------------------------------------------------------
# Sub-Nav
# --------------------------------------------------------------------------


class TestSubNavScrollsInsideItsBar:
    def _narrow(self) -> str:
        _, blocks = _split_media(render_sub_nav_css(), _below("web.layout.bp-tablet"))
        assert blocks, "Sub-Nav hat keinen Block unter bp-tablet"
        return "".join(blocks)

    def test_bar_scrolls_horizontally_when_narrow(self):
        body = _rule(self._narrow(), ".mn-sub-nav__inner")
        assert "overflow-x: auto" in body

    def test_scrollbar_is_unobtrusive_but_not_hidden(self):
        body = _rule(self._narrow(), ".mn-sub-nav__inner")
        assert "scrollbar-width: thin" in body
        assert "scrollbar-width: none" not in body

    def test_tabs_keep_their_size_and_do_not_wrap(self):
        body = _rule(self._narrow(), ".mn-sub-nav__tab")
        assert "flex: none" in body
        assert "white-space: nowrap" in body

    def test_desktop_rules_are_untouched(self):
        outside, _ = _split_media(render_sub_nav_css(), _below("web.layout.bp-tablet"))
        inner = _rule(outside, ".mn-sub-nav__inner")
        tab = _rule(outside, ".mn-sub-nav__tab")
        assert inner and tab
        assert "overflow" not in inner and "scrollbar" not in inner
        assert "nowrap" not in tab and "flex:" not in tab
        assert "display: flex" in inner
        assert "display: inline-block" in tab

    def test_breakpoint_comes_from_token_not_a_literal(self):
        css = render_sub_nav_css()
        assert f"@media ({_below('web.layout.bp-tablet')})" in css


# --------------------------------------------------------------------------
# Card-Grid
# --------------------------------------------------------------------------


class TestCardGridCollapsesOnNarrowViewports:
    def test_desktop_rule_is_unchanged(self):
        css = render_card_grid_css()
        outside, _ = _split_media(css, _below("web.layout.bp-tablet"))
        outside, _ = _split_media(outside, _below("web.layout.bp-mobile"))
        body = _rule(outside, ".mn-card-grid")
        assert "display: grid" in body
        assert "grid-template-columns: repeat(var(--mn-card-grid-cols, 3), 1fr)" in body
        assert "gap: var(--space-4, 16px)" in body

    def test_below_mobile_is_one_column(self):
        _, blocks = _split_media(render_card_grid_css(), _below("web.layout.bp-mobile"))
        assert len(blocks) == 1
        body = _rule(blocks[0], ".mn-card-grid")
        assert re.search(
            r"grid-template-columns:\s*(1fr|minmax\(0,\s*1fr\)|repeat\(1,[^)]*\))\s*;",
            body,
        ), body

    def test_below_tablet_reads_the_tablet_column_variable(self):
        """Tablet-Regel: die Spaltenzahl kommt aus --mn-card-grid-cols-tablet,
        ohne diese Variable (aelteres Markup) aus --mn-card-grid-cols."""
        _, blocks = _split_media(render_card_grid_css(), _below("web.layout.bp-tablet"))
        assert len(blocks) == 1
        body = _rule(blocks[0], ".mn-card-grid")
        assert (
            "grid-template-columns: repeat(var(--mn-card-grid-cols-tablet, "
            "var(--mn-card-grid-cols, 3)), 1fr)"
        ) in body, body

    def test_no_css_min_inside_repeat(self):
        """repeat() bekommt keine CSS-Math-Funktion als Zaehler — die
        Browser-Unterstuetzung (Safari) ist nicht belegt."""
        assert not re.search(
            r"repeat\(\s*(min|max|clamp|calc)\(", render_card_grid_css()
        )

    def test_cascade_mobile_comes_after_tablet(self):
        """Gleiche Spezifitaet, spaeter gewinnt: mobil MUSS hinter tablet stehen."""
        css = render_card_grid_css()
        tablet = css.index(f"@media ({_below('web.layout.bp-tablet')})")
        mobile = css.index(f"@media ({_below('web.layout.bp-mobile')})")
        assert tablet < mobile

    def test_tablet_and_mobile_use_the_same_selector(self):
        """Gleicher Selektor = gleiche Spezifitaet; die Reihenfolge entscheidet."""
        css = render_card_grid_css()
        _, tablet = _split_media(css, _below("web.layout.bp-tablet"))
        _, mobile = _split_media(css, _below("web.layout.bp-mobile"))
        assert _rule(tablet[0], ".mn-card-grid") and _rule(mobile[0], ".mn-card-grid")


class TestCardGridRendersTabletColumns:
    """Der Renderer rechnet die Tablet-Spaltenzahl in Python aus: min(columns, 2)."""

    @pytest.mark.parametrize(("columns", "tablet"), [(1, 1), (2, 2), (3, 2), (4, 2)])
    def test_tablet_columns_are_capped_at_two(self, columns, tablet):
        grid = CardGridInput(
            cards=[ContentCardInput(title="A", body="B")], columns=columns
        )
        html = render_card_grid_html(grid)
        assert f"--mn-card-grid-cols:{columns}" in html
        assert f"--mn-card-grid-cols-tablet:{tablet}" in html

    def test_both_variables_live_in_the_same_inline_style(self):
        grid = CardGridInput(cards=[ContentCardInput(title="A", body="B")], columns=4)
        html = render_card_grid_html(grid)
        assert (
            '<div class="mn-card-grid" '
            'style="--mn-card-grid-cols:4;--mn-card-grid-cols-tablet:2">'
        ) in html


class TestCardGridInlineCss:
    def test_inline_css_carries_the_responsive_rules(self):
        grid = CardGridInput(cards=[ContentCardInput(title="A", body="B")], columns=4)
        html = render_card_grid_html(grid, inline_css=True)
        assert f"@media ({_below('web.layout.bp-mobile')})" in html
        assert f"@media ({_below('web.layout.bp-tablet')})" in html


# --------------------------------------------------------------------------
# Browser-Beweis (Wirkung) — nur mit Playwright + Chromium
# --------------------------------------------------------------------------

_FONTS = Path(__import__("mn_design_system").__file__).parent / "fonts"
_TOKENS_CSS = Path(__import__("mn_design_system").__file__).parent.parent / (
    "dist/css/tokens.css"
)

_EMBLEM = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' "
    "width='32' height='32'><rect width='32' height='32' fill='%23888'/></svg>"
)
_TABS = [
    "Uebersicht",
    "Gesundheit",
    "Erbschaft",
    "Rotary",
    "Beziehungen",
    "Kalender",
    "Dokumente",
    "Einstellungen",
]


def _page(columns: int) -> str:
    """Testseite wie der Konsument sie baut: Masthead (4 Pillen + 2 Chips),
    Sub-Nav (8 Tabs), Card-Grid, dazu die Konsumenten-Grundregeln."""
    masthead = MastheadInput(
        emblem=MastheadEmblem(src=_EMBLEM, alt="Emblem", href="/start/"),
        wordmark="from the desk of mn",
        edition_date="Samstag · 3. Oktober 2026",
        tier_items=[
            MastheadTierItem(
                label="Start", href="/start/", tier=WebTier.START, active=True
            ),
            MastheadTierItem(
                label="Bibliothek", href="/bibliothek/", tier=WebTier.BIBLIOTHEK
            ),
            MastheadTierItem(label="Atelier", href="/atelier/", tier=WebTier.ATELIER),
            MastheadTierItem(
                label="Kabinett", href="/kabinett/", tier=WebTier.KABINETT
            ),
        ],
        context_chip=MastheadChip(tier=WebTier.START, label="Start · GREEN"),
        user_chip_id="user-chip",
        user_chip_label="Owner · RED",
    )
    sub_nav = SubNavInput(
        tier=WebTier.KABINETT,
        tabs=[
            SubNavTab(label=t, href=f"#{t}", active=i == 5) for i, t in enumerate(_TABS)
        ],
    )
    cards = [
        ContentCardInput(
            title=f"Karte {i + 1}: Reisefotografie",
            body="Eine Auswahl aus zehn Jahren unterwegs, geordnet nach Orten.",
            href=f"#k{i}",
            tier=WebTier.BIBLIOTHEK,
        )
        for i in range(8)
    ]
    grid = CardGridInput(cards=cards, columns=columns)
    faces = "".join(
        f'@font-face{{font-family:"Geist";font-weight:{w};'
        f'src:url("{(_FONTS / "geist" / f"Geist-{n}.ttf").as_uri()}");}}'
        for w, n in ((400, "Regular"), (500, "Medium"), (700, "Bold"))
    )
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{faces}
{_TOKENS_CSS.read_text()}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "Geist", system-ui, sans-serif; font-size: 16px; }}
main {{ max-width: var(--web-layout-content-width, 1024px); margin-inline: auto;
  padding: 24px var(--web-layout-page-inset, 44px); }}
{render_foundation_css()}
{render_masthead_css()}
{render_sub_nav_css()}
{render_content_card_css()}
{render_card_grid_css()}
</style></head><body>
{render_masthead_html(masthead)}
{render_sub_nav_html(sub_nav)}
<main>{render_card_grid_html(grid)}</main>
</body></html>"""


_MEASURE = """() => {
  const de = document.documentElement;
  const box = (s) => document.querySelector(s).getBoundingClientRect();
  const tops = (s) => new Set([...document.querySelectorAll(s)]
    .map(e => Math.round(e.getBoundingClientRect().top)));
  const lefts = new Set([...document.querySelectorAll('.mn-card-grid > .mn-content-card')]
    .map(e => Math.round(e.getBoundingClientRect().left)));
  const bar = document.querySelector('.mn-sub-nav__inner');
  const chips = [...document.querySelectorAll('.mn-masthead__chip')]
    .map(e => e.getBoundingClientRect());
  return {
    scrollWidth: de.scrollWidth, clientWidth: de.clientWidth,
    pillRows: tops('.mn-masthead__pill').size,
    // umgebrochen = die Kontext-Zeile beginnt unterhalb der Pillen-Zeile
    chipsBelowPills: box('.mn-masthead__context').top >= box('.mn-masthead__pills').bottom - 0.5,
    chipRightMax: Math.max(...chips.map(r => r.right)),
    tabRows: tops('.mn-sub-nav__tab').size,
    barScrollWidth: bar.scrollWidth, barClientWidth: bar.clientWidth,
    barOverflowX: getComputedStyle(bar).overflowX,
    gridCols: lefts.size,
  };
}"""


@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright nicht installiert — Wirkung UNGEPRUEFT",
    )
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except sync_api.Error as exc:  # Chromium fehlt: sichtbar ueberspringen
            pytest.skip(f"Chromium nicht startbar — Wirkung UNGEPRUEFT ({exc!s:.80})")
        yield b
        b.close()


def _measure(browser, tmp_path, columns: int, width: int) -> dict:
    page_file = tmp_path / f"page-{columns}.html"
    page_file.write_text(_page(columns), encoding="utf-8")
    ctx = browser.new_context(viewport={"width": width, "height": 900})
    try:
        page = ctx.new_page()
        page.goto(page_file.as_uri())
        page.evaluate("document.fonts.ready")
        return page.evaluate(_MEASURE)
    finally:
        ctx.close()


class TestBrowserProof:
    @pytest.mark.parametrize("width", [390, 360])
    def test_no_horizontal_page_scroll_on_phone(self, browser, tmp_path, width):
        m = _measure(browser, tmp_path, 4, width)
        assert m["scrollWidth"] <= m["clientWidth"], m

    def test_masthead_chips_wrap_below_pills_on_phone(self, browser, tmp_path):
        m = _measure(browser, tmp_path, 4, 390)
        assert m["pillRows"] == 1, m
        assert m["chipsBelowPills"], m
        assert m["chipRightMax"] <= m["clientWidth"], m

    def test_sub_nav_scrolls_inside_its_bar_on_phone(self, browser, tmp_path):
        m = _measure(browser, tmp_path, 4, 390)
        assert m["tabRows"] == 1, m
        assert m["barScrollWidth"] > m["barClientWidth"], m
        # scrollWidth > clientWidth gilt auch fuer eine ueberlaufende, NICHT
        # scrollbare Leiste — erst overflow-x: auto macht sie zur Scroll-Leiste.
        assert m["barOverflowX"] == "auto", m

    @pytest.mark.parametrize(
        ("columns", "width", "expected"),
        [
            (4, 390, 1),
            (3, 390, 1),
            (2, 390, 1),
            (1, 390, 1),
            (4, 768, 2),
            (3, 768, 2),
            (2, 768, 2),
            (1, 768, 1),  # ein Raster mit 1 Spalte bleibt auch auf dem Tablet eines
            (4, 1440, 4),
            (3, 1440, 3),
            (2, 1440, 2),
            (1, 1440, 1),
        ],
    )
    def test_card_grid_columns_per_width(
        self, browser, tmp_path, columns, width, expected
    ):
        m = _measure(browser, tmp_path, columns, width)
        assert m["gridCols"] == expected, m

    @pytest.mark.parametrize("width", [640, 1023, 1024, 1440])
    def test_breakpoint_edges_follow_the_tokens(self, browser, tmp_path, width):
        """640 = Tablet (2 Spalten), 1023 = Tablet, 1024 und mehr = Desktop."""
        m = _measure(browser, tmp_path, 4, width)
        assert m["gridCols"] == {640: 2, 1023: 2, 1024: 4, 1440: 4}[width], m

    def test_desktop_keeps_one_row_masthead_and_one_row_tabs(self, browser, tmp_path):
        m = _measure(browser, tmp_path, 4, 1440)
        assert m["scrollWidth"] <= m["clientWidth"], m
        assert not m["chipsBelowPills"], m
        assert m["tabRows"] == 1, m
