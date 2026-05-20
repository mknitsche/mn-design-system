"""Web-Renderer (HTML + CSS-Custom-Property-Tokens) — Welle E.0 (S238).

Konsumiert dieselben Pydantic-Contracts wie der pdf/-Renderer
(`mn_design_system.components._patterns.contracts`).

Output: HTML-Strings, die mit `dist/css/tokens.css` als CSS-Variablen-Quelle
zusammenarbeiten. Konsumenten muessen `tokens.css` in ihren Build-Output
einbinden:

    <link rel="stylesheet" href="path/to/tokens.css">

Komponenten-spezifisches CSS (Layout, nicht Token-Werte) wird inline pro
Komponente geliefert (`render_kpi_card_css()`-Funktion). So kann ein
Konsument entweder:
  (a) das CSS einmal in seinen Build-Output schreiben (`render_*_css()` aufrufen,
      Output cachen), oder
  (b) inline pro HTML-Snippet einbinden (`render_kpi_card_html(input, inline_css=True)`).

Status: Erst-Implementierung (Welle E.0). Foto-Homepage ist erster Konsument
ab PRJ-9.
"""

from mn_design_system.components.web.brand_bar import (
    render_brand_bar_css,
    render_brand_bar_html,
)
from mn_design_system.components.web.kpi_card import (
    render_kpi_card_css,
    render_kpi_card_html,
)
from mn_design_system.components.web.sparkline import render_sparkline_svg
from mn_design_system.components.web.sub_nav import (
    render_sub_nav_css,
    render_sub_nav_html,
)
from mn_design_system.components.web.tier_chip import (
    render_tier_chip_css,
    render_tier_chip_html,
)
from mn_design_system.components.web.wetter_strip import (
    render_wetter_strip_css,
    render_wetter_strip_html,
)

__all__ = [
    "render_brand_bar_css",
    "render_brand_bar_html",
    "render_kpi_card_css",
    "render_kpi_card_html",
    "render_sparkline_svg",
    "render_sub_nav_css",
    "render_sub_nav_html",
    "render_tier_chip_css",
    "render_tier_chip_html",
    "render_wetter_strip_css",
    "render_wetter_strip_html",
]
