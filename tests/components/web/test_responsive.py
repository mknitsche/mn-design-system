"""Responsive-Verhalten auf schmalen Viewports (0.14.1 Handy-Breite 390 px, 0.14.2 Feinschliff).

0.14.1: Drei Komponenten liefen auf dem Handy ueber den Bildschirm und erzeugten
horizontalen Seiten-Scroll: die Kontext-Chips des Masthead, die Tab-Zeile der
Sub-Nav und das Card-Grid mit fester Spaltenzahl.

0.14.2: (a) die scrollbare Sub-Nav zeigt an ihren Raendern, dass es weitergeht
(Rand-Hinweis, nur wo wirklich Inhalt ueberlaeuft), und der aktive Reiter steht
beim Laden im Ausschnitt (CSS `scroll-initial-target`, dazu ein kleines externes
Skript fuer Browser ohne diese Property); (b) die Tier-Pillen des Masthead
verbreitern die Seite bei 320 px nicht mehr.

Zwei Ebenen, weil jede allein luegt:

- CSS-Struktur (immer): die Regeln stehen in der richtigen Media-Query, die
  Desktop-Regeln sind unveraendert, die Breakpoints kommen aus den Tokens.
  Das beweist die Schreibweise, nicht die Wirkung.
- Browser-Wirkung (nur mit Playwright + Chromium; sonst sichtbar uebersprungen,
  nie still gruen): eine echte Seite wird bei 1440/768/390 px gemessen.
  Das beweist die Wirkung, ersetzt aber nicht die schnellen Struktur-Tests.
"""

from __future__ import annotations

import http.server
import io
import re
import threading
from pathlib import Path

import pytest
from PIL import Image

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


def _js() -> str:
    """Skript-Renderer der Sub-Nav. Der Import steht hier, nicht oben: fehlt der
    Renderer, soll NUR dieser Test rot werden, nicht das ganze Modul."""
    from mn_design_system.components.web import sub_nav

    return sub_nav.render_sub_nav_js()


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

    def test_pills_wrap_instead_of_overflowing(self):
        """0.14.2: passen die Pillen nicht in eine Zeile (320 px), brechen sie um,
        statt die Seite zu verbreitern. Wo sie passen, bleibt es EINE Zeile —
        das beweist der Browser-Test (390 px), nicht diese Regel."""
        body = _rule(render_masthead_css(), ".mn-masthead__pills")
        assert "flex-wrap: wrap" in body

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
        pills = _rule(css, ".mn-masthead__pills")
        for decl in (
            "display: flex",
            "align-items: center",
            "gap: var(--space-1, 4px)",
        ):
            assert decl in pills
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
        # 0.14.2: Rand-Hinweis und Scroll-Ziel gibt es nur auf dem Handy
        assert "background" not in inner and "scroll-" not in inner
        assert "scroll-" not in tab
        assert not _rule(outside, ".mn-sub-nav__tab.is-active")
        assert "display: flex" in inner
        assert "display: inline-block" in tab

    def test_breakpoint_comes_from_token_not_a_literal(self):
        css = render_sub_nav_css()
        assert f"@media ({_below('web.layout.bp-tablet')})" in css


class TestSubNavEdgeHint:
    """0.14.2 (a): die Leiste zeigt, dass es weitergeht — nur wo Inhalt ueberlaeuft.

    Klassische "Scroll-Schatten": zwei mitscrollende Deckflaechen (`local`) in
    Flaechenfarbe verdecken zwei am Rand stehende Schatten (`scroll`); sie geben
    den Schatten genau dort frei, wo hinter dem Rand noch Inhalt liegt. Reines CSS,
    kein Skript. Die WIRKUNG beweisen die Browser-Tests (Pixelprobe am Rand).
    """

    def _narrow(self) -> str:
        _, blocks = _split_media(render_sub_nav_css(), _below("web.layout.bp-tablet"))
        return "".join(blocks)

    def _bar(self) -> str:
        return _rule(self._narrow(), ".mn-sub-nav__inner")

    def _decl(self, name: str) -> str:
        m = re.search(rf"{name}:\s*([^;]+);", self._bar())
        assert m, f"{name} fehlt in {self._bar()!r}"
        return m.group(1)

    def test_two_cover_layers_and_two_shadow_layers(self):
        layers = [x.strip() for x in self._decl("background-attachment").split(",")]
        assert sorted(layers) == ["local", "local", "scroll", "scroll"]
        assert self._decl("background-image").count("linear-gradient(") == 4

    def test_covers_match_the_bar_surface(self):
        """Die Deckflaechen muessen die Flaechenfarbe der Sub-Nav tragen, sonst
        wuerden sie als Streifen sichtbar."""
        assert "var(--color-light-surface" in self._decl("background-image")
        assert "var(--color-light-surface" in self._decl("background-color")

    def test_hint_values_come_from_tokens(self):
        """Keine Hartwerte: nach Abzug der var()-Fallbacks bleibt keine Farbe
        und keine Pixelzahl uebrig."""
        for name in ("background-image", "background-size", "background-color"):
            rest = re.sub(r"var\([^)]*\)", "", self._decl(name))
            assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|\d+px", rest), (
                name,
                rest,
            )

    def test_no_motion_is_introduced(self):
        """prefers-reduced-motion: der Hinweis ist statisch, es gibt keine
        Animation und kein weiches Scrollen."""
        narrow = self._narrow()
        for word in ("transition", "animation", "scroll-behavior"):
            assert word not in narrow, word


class TestSubNavActiveTabAsInitialTarget:
    """0.14.2 (b): der aktive Reiter steht beim Laden im Ausschnitt (CSS)."""

    def _active(self) -> str:
        _, blocks = _split_media(render_sub_nav_css(), _below("web.layout.bp-tablet"))
        return _rule("".join(blocks), ".mn-sub-nav__tab.is-active")

    def test_active_tab_is_the_initial_scroll_target(self):
        assert "scroll-initial-target: nearest" in self._active()

    def test_active_tab_is_centred(self):
        """Ohne `scroll-snap-align` setzt der Browser den Reiter an den linken
        Rand (gemessen) — zentriert zeigt er beide Nachbarn."""
        assert "scroll-snap-align: center" in self._active()


class TestSubNavScript:
    """0.14.2 (b): Rueckfall fuer Browser ohne `scroll-initial-target` (Safari,
    Firefox). Ein externes, CSP-taugliches Skript — nie ein Inline-Skript."""

    def test_is_one_self_contained_function(self):
        js = _js().strip()
        assert js.startswith("(function") and js.endswith("})();"), js

    def test_touches_only_the_bar(self):
        js = _js()
        assert ".mn-sub-nav__inner" in js and "scrollLeft" in js
        for forbidden in (
            "scrollIntoView",  # rollt auch Vorfahren: die Seite wuerde springen
            "smooth",  # keine Animation (prefers-reduced-motion)
            "window.scroll",
            "location",
            "innerHTML",
            "eval(",
            "document.write",
            "<script",
        ):
            assert forbidden not in js, forbidden


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


def _page(
    columns: int,
    *,
    active_tab: int = 5,
    active_tier: int = 0,
    tabs: list[str] | None = None,
    head_extra: str = "",
    strip_css: tuple[str, ...] = (),
) -> str:
    """Testseite wie der Konsument sie baut: Masthead (4 Pillen + 2 Chips),
    Sub-Nav (8 Tabs), Card-Grid, dazu die Konsumenten-Grundregeln.

    active_tab / active_tier waehlen den aktiven Reiter bzw. die aktive Pille;
    head_extra haengt Markup in den <head> (z. B. das Sub-Nav-Skript);
    strip_css entfernt Deklarationen aus dem Komponenten-CSS — damit simuliert
    ein Test einen Browser, der sie nicht kennt. Fehlt die Deklaration, bricht
    die Seite ab: eine Simulation, die nichts veraendert, ist keine."""
    tabs = _TABS if tabs is None else tabs
    masthead = MastheadInput(
        emblem=MastheadEmblem(src=_EMBLEM, alt="Emblem", href="/start/"),
        wordmark="from the desk of mn",
        edition_date="Samstag · 3. Oktober 2026",
        tier_items=[
            MastheadTierItem(
                label=label,
                href=f"/{label.lower()}/",
                tier=tier,
                active=i == active_tier,
            )
            for i, (label, tier) in enumerate(
                [
                    ("Start", WebTier.START),
                    ("Bibliothek", WebTier.BIBLIOTHEK),
                    ("Atelier", WebTier.ATELIER),
                    ("Kabinett", WebTier.KABINETT),
                ]
            )
        ],
        context_chip=MastheadChip(tier=WebTier.START, label="Start · GREEN"),
        user_chip_id="user-chip",
        user_chip_label="Owner · RED",
    )
    sub_nav = SubNavInput(
        tier=WebTier.KABINETT,
        tabs=[
            SubNavTab(label=t, href=f"#{t}", active=i == active_tab)
            for i, t in enumerate(tabs)
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
    components_css = "\n".join(
        [
            render_foundation_css(),
            render_masthead_css(),
            render_sub_nav_css(),
            render_content_card_css(),
            render_card_grid_css(),
        ]
    )
    for decl in strip_css:
        assert decl in components_css, f"strip_css: {decl!r} nicht im CSS"
        components_css = components_css.replace(decl, "")
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
{components_css}
</style>{head_extra}</head><body>
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
    // 0.14.2: Masthead-Pillen, aktiver Reiter, Seiten-Scroll-Position
    mastheadScrollWidth: document.querySelector('.mn-masthead').scrollWidth,
    pillsScrollWidth: document.querySelector('.mn-masthead__pills').scrollWidth,
    pillsClientWidth: document.querySelector('.mn-masthead__pills').clientWidth,
    pillRightMax: Math.max(...[...document.querySelectorAll('.mn-masthead__pill')]
      .map(e => e.getBoundingClientRect().right)),
    barScrollLeft: bar.scrollLeft,
    activeLeft: box('.mn-sub-nav__tab.is-active').left - bar.getBoundingClientRect().left,
    activeRight: box('.mn-sub-nav__tab.is-active').right - bar.getBoundingClientRect().left,
    pageScrollX: window.scrollX, pageScrollY: window.scrollY,
    inlineRan: window.__inlineRan === true,
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


def _measure(browser, tmp_path, columns: int, width: int, **page_kwargs) -> dict:
    page_file = tmp_path / f"page-{columns}.html"
    page_file.write_text(_page(columns, **page_kwargs), encoding="utf-8")
    return _measure_url(browser, page_file.as_uri(), width)


def _measure_url(browser, url: str, width: int) -> dict:
    ctx = browser.new_context(viewport={"width": width, "height": 900})
    try:
        page = ctx.new_page()
        page.goto(url)
        page.evaluate("document.fonts.ready")
        return page.evaluate(_MEASURE)
    finally:
        ctx.close()


@pytest.fixture
def csp_server(tmp_path):
    """Liefert tmp_path ueber HTTP mit `Content-Security-Policy: script-src 'self'`
    — so streng wie der Konsument (kein 'unsafe-inline')."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(tmp_path), **kwargs)

        def end_headers(self):
            self.send_header("Content-Security-Policy", "script-src 'self'")
            super().end_headers()

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


class TestBrowserProof:
    @pytest.mark.parametrize("width", [390, 360, 320])
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


# --------------------------------------------------------------------------
# 0.14.2 — Masthead-Pillen bei 320 px, Sub-Nav-Rand-Hinweis, aktiver Reiter
# --------------------------------------------------------------------------

_INITIAL_TARGET = "scroll-initial-target: nearest;"


def _rgb(token: str) -> tuple[int, int, int]:
    h = get(token).lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _in_view(m: dict) -> bool:
    return m["activeLeft"] >= 0 and m["activeRight"] <= m["barClientWidth"]


def _centred(m: dict, tolerance: float = 2) -> bool:
    centre = (m["activeLeft"] + m["activeRight"]) / 2
    return abs(centre - m["barClientWidth"] / 2) <= tolerance


class TestMastheadPillsFitOnSmallestPhones:
    """320 px (iPhone SE, kleine Android): die vier Tier-Pillen duerfen die Seite
    nicht verbreitern — gemessen vor dem Fix: Pillen-Zeile 9 px zu breit."""

    @pytest.mark.parametrize("active_tier", [0, 1, 2, 3])
    def test_no_overflow_for_every_active_tier(self, browser, tmp_path, active_tier):
        m = _measure(browser, tmp_path, 4, 320, active_tier=active_tier)
        assert m["scrollWidth"] <= m["clientWidth"], m
        assert m["mastheadScrollWidth"] <= m["clientWidth"], m
        assert m["pillsScrollWidth"] <= m["pillsClientWidth"], m
        assert m["pillRightMax"] <= m["clientWidth"], m
        assert m["chipRightMax"] <= m["clientWidth"], m

    @pytest.mark.parametrize("width", [390, 360])
    def test_pills_stay_one_row_where_they_fit(self, browser, tmp_path, width):
        """Der Umbruch ist ein Sicherheitsnetz, kein neues Aussehen: wo die Pillen
        passen (alle gaengigen Handys ab 350 px), bleiben sie eine Zeile."""
        m = _measure(browser, tmp_path, 4, width)
        assert m["pillRows"] == 1, m


class TestSubNavEdgeHintInBrowser:
    """0.14.2 (a): Pixelprobe am Rand der Leiste. Die Probe liegt in der oberen
    Polsterung der Leiste (kein Reiter, kein Text) — dort steht NUR der Hintergrund,
    also Flaechenfarbe (kein Hinweis) oder Schatten (Hinweis)."""

    SURFACE = _rgb("color.light.surface")

    def _edges(self, browser, tmp_path, scroll_to: str, tabs=None):
        page_file = tmp_path / "hint.html"
        page_file.write_text(_page(4, tabs=tabs), encoding="utf-8")
        ctx = browser.new_context(viewport={"width": 390, "height": 900})
        try:
            page = ctx.new_page()
            page.goto(page_file.as_uri())
            page.evaluate("document.fonts.ready")
            top, scrollable = page.evaluate(
                """(to) => {
                  const bar = document.querySelector('.mn-sub-nav__inner');
                  const max = bar.scrollWidth - bar.clientWidth;
                  bar.scrollLeft = {start: 0, middle: max / 2, end: max}[to];
                  return [bar.getBoundingClientRect().top + 2, max > 0];
                }""",
                scroll_to,
            )
            png = page.screenshot(
                clip={"x": 0, "y": top - 2, "width": 390, "height": 6}
            )
            im = Image.open(io.BytesIO(png)).convert("RGB")
            return im.getpixel((0, 2)), im.getpixel((389, 2)), scrollable
        finally:
            ctx.close()

    @pytest.mark.parametrize(
        ("scroll_to", "hint_left", "hint_right"),
        [
            ("start", False, True),  # links ist nichts verdeckt, rechts geht es weiter
            ("middle", True, True),
            ("end", True, False),
        ],
    )
    def test_hint_only_towards_hidden_content(
        self, browser, tmp_path, scroll_to, hint_left, hint_right
    ):
        left, right, scrollable = self._edges(browser, tmp_path, scroll_to)
        assert scrollable, "die Leiste muss hier ueberlaufen — sonst beweist das nichts"
        for name, px, expected in (
            ("links", left, hint_left),
            ("rechts", right, hint_right),
        ):
            if expected:
                assert px != self.SURFACE and sum(px) < sum(self.SURFACE), (name, px)
            else:
                assert px == self.SURFACE, (name, px)

    def test_no_hint_when_everything_fits(self, browser, tmp_path):
        left, right, scrollable = self._edges(
            browser, tmp_path, "start", tabs=["Uebersicht", "Profil"]
        )
        assert not scrollable, "zwei Reiter muessen bei 390 px passen"
        assert left == self.SURFACE and right == self.SURFACE, (left, right)


class TestSubNavActiveTabInViewOnLoad:
    """0.14.2 (b), nur CSS (Chromium kennt `scroll-initial-target`): der aktive
    Reiter steht beim Laden im Ausschnitt, die Seite springt dabei nicht."""

    @pytest.fixture(autouse=True)
    def _needs_initial_target(self, browser):
        ctx = browser.new_context()
        try:
            ok = ctx.new_page().evaluate(
                "CSS.supports('scroll-initial-target', 'nearest')"
            )
        finally:
            ctx.close()
        if not ok:
            pytest.skip(
                "Chromium kennt scroll-initial-target nicht — Wirkung UNGEPRUEFT"
            )

    @pytest.mark.parametrize("width", [390, 320])
    @pytest.mark.parametrize("active_tab", [0, 5, 7])
    def test_active_tab_is_in_view(self, browser, tmp_path, width, active_tab):
        m = _measure(browser, tmp_path, 4, width, active_tab=active_tab)
        assert m["barScrollWidth"] > m["barClientWidth"], m
        assert _in_view(m), m
        assert m["pageScrollX"] == 0 and m["pageScrollY"] == 0, m

    @pytest.mark.parametrize("width", [390, 320])
    def test_a_middle_tab_is_centred(self, browser, tmp_path, width):
        m = _measure(browser, tmp_path, 4, width, active_tab=5)
        assert _centred(m), m

    def test_without_the_property_the_active_tab_stays_out_of_view(
        self, browser, tmp_path
    ):
        """Gegenprobe: dieselbe Seite ohne die Property. Ohne sie waere der Test
        oben auch gruen, wenn der Reiter ohnehin sichtbar waere."""
        m = _measure(
            browser, tmp_path, 4, 390, active_tab=7, strip_css=(_INITIAL_TARGET,)
        )
        assert not _in_view(m), m


class TestSubNavScriptInBrowser:
    """0.14.2 (b), Rueckfall: Browser ohne `scroll-initial-target` (Safari, Firefox).
    Simuliert durch Entfernen der Property; das Skript kommt als EXTERNE Datei
    unter `Content-Security-Policy: script-src 'self'`."""

    SCRIPT = '<script src="/mn-sub-nav.js" defer></script>'
    INLINE = "<script>window.__inlineRan = true</script>"

    def _serve(self, tmp_path, **kwargs):
        (tmp_path / "page.html").write_text(
            _page(4, strip_css=(_INITIAL_TARGET,), **kwargs), encoding="utf-8"
        )
        (tmp_path / "mn-sub-nav.js").write_text(_js(), encoding="utf-8")

    def test_script_centres_the_active_tab_under_a_strict_csp(
        self, browser, tmp_path, csp_server
    ):
        self._serve(tmp_path, active_tab=5, head_extra=self.SCRIPT + self.INLINE)
        m = _measure_url(browser, f"{csp_server}/page.html", 390)
        assert not m["inlineRan"], "CSP wirkt nicht — der Beweis waere wertlos"
        assert _in_view(m) and _centred(m), m
        assert m["pageScrollX"] == 0 and m["pageScrollY"] == 0, m

    @pytest.mark.parametrize("active_tab", [0, 7])
    def test_script_keeps_the_ends_in_view(
        self, browser, tmp_path, csp_server, active_tab
    ):
        self._serve(tmp_path, active_tab=active_tab, head_extra=self.SCRIPT)
        m = _measure_url(browser, f"{csp_server}/page.html", 390)
        assert _in_view(m), m

    def test_without_the_script_the_active_tab_is_out_of_view(
        self, browser, tmp_path, csp_server
    ):
        """Gegenprobe zu den Tests oben: gleiche Seite, nur ohne <script>."""
        self._serve(tmp_path, active_tab=7)
        m = _measure_url(browser, f"{csp_server}/page.html", 390)
        assert not _in_view(m), m

    def test_script_moves_only_the_bar_never_the_page(self, browser, tmp_path):
        page_file = tmp_path / "page.html"
        page_file.write_text(
            _page(4, active_tab=7, strip_css=(_INITIAL_TARGET,)), encoding="utf-8"
        )
        ctx = browser.new_context(viewport={"width": 390, "height": 600})
        try:
            page = ctx.new_page()
            page.goto(page_file.as_uri())
            page.evaluate("document.fonts.ready")
            page.evaluate("window.scrollTo(0, 200)")
            before = page.evaluate("[scrollX, scrollY]")
            page.evaluate(_js())
            after = page.evaluate("[scrollX, scrollY]")
            m = page.evaluate(_MEASURE)
        finally:
            ctx.close()
        assert before == after == [0, 200], (before, after)
        assert _in_view(m), m
