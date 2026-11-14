"""Gemeinsame Browser-Hilfe fuer die Web-Tests ab 0.24.0 (Wirkung statt Schreibweise).

Nur mit Playwright + Chromium; sonst sichtbar uebersprungen (UNGEPRUEFT), nie still gruen.
Aeltere Browser-Tests haben eine eigene ``browser``-Fixture im Modul; die gewinnt dort.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import mn_design_system

_REPO = Path(mn_design_system.__file__).parents[1]


@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright nicht installiert — Wirkung UNGEPRUEFT",
    )
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except sync_api.Error as exc:
            pytest.skip(f"Chromium nicht startbar — Wirkung UNGEPRUEFT ({exc!s:.80})")
        yield b
        b.close()


@pytest.fixture
def seite_laden(browser, tmp_path):
    """Liefert ``laden(koerper, css, breite=390) -> (ctx, page)``; der Aufrufer schliesst ``ctx``."""

    def laden(koerper: str, css: str, breite: int = 390, hoehe: int = 800):
        tokens = (_REPO / "dist" / "css" / "tokens.css").read_text(encoding="utf-8")
        html = (
            '<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f"<style>{tokens}\n{css}</style></head><body>{koerper}</body></html>"
        )
        datei = tmp_path / "seite.html"
        datei.write_text(html, encoding="utf-8")
        ctx = browser.new_context(viewport={"width": breite, "height": hoehe})
        page = ctx.new_page()
        page.goto(datei.as_uri())
        page.evaluate("document.fonts.ready")
        return ctx, page

    return laden
