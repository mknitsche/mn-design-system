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

from mn_design_system.components.web.content_card import (
    render_card_grid_css,
    render_card_grid_html,
    render_content_card_css,
    render_content_card_html,
)
from mn_design_system.components.web.empty_state import (
    render_empty_state_css,
    render_empty_state_html,
)
from mn_design_system.components.web.foundation import (
    render_foundation_css,
    render_initiale_css,
)
from mn_design_system.components.web.footer import (
    render_footer_css,
    render_footer_html,
)
from mn_design_system.components.web.kpi_card import (
    render_kpi_card_css,
    render_kpi_card_html,
)
from mn_design_system.components.web.masthead import (
    render_masthead_css,
    render_masthead_html,
)
from mn_design_system.components.web.page_header import (
    render_page_header_css,
    render_page_header_html,
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
    "render_card_grid_css",
    "render_card_grid_html",
    "render_content_card_css",
    "render_content_card_html",
    "render_empty_state_css",
    "render_empty_state_html",
    "render_foundation_css",
    "render_footer_css",
    "render_footer_html",
    "render_initiale_css",
    "render_kpi_card_css",
    "render_kpi_card_html",
    "render_masthead_css",
    "render_masthead_html",
    "render_page_header_css",
    "render_page_header_html",
    "render_sparkline_svg",
    "render_sub_nav_css",
    "render_sub_nav_html",
    "render_tier_chip_css",
    "render_tier_chip_html",
    "render_wetter_strip_css",
    "render_wetter_strip_html",
]
