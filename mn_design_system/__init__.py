"""MN PKA Design-System — Tokens, Fonts, Komponenten.

Public-API:
    from mn_design_system import (
        # Token-Helpers (v0.4.4+)
        space_token, size_token, leading_token, color_token,
        font_family, font_with_fallback, token,
        # Konstanten
        TOKENS, MM_TO_PT, MM_TO_PX,
    )
    from mn_design_system.tokens import TOKENS, get
    from mn_design_system.fonts import register_all_fonts, FONT_DIR

Komponenten (Welle B):
    from mn_design_system.components.pdf import build_sparkline, build_kpi_card, build_wetter_strip

Versionierung: SemVer ab v0.1.0 (Welle A).
"""

from .helpers import (
    MM_TO_PT,
    MM_TO_PX,
    TOKENS,
    color_token,
    font_family,
    font_with_fallback,
    leading_token,
    size_token,
    space_token,
    token,
)

__version__ = "0.5.0"

__all__ = [
    "__version__",
    "TOKENS",
    "MM_TO_PT",
    "MM_TO_PX",
    "space_token",
    "size_token",
    "leading_token",
    "color_token",
    "font_family",
    "font_with_fallback",
    "token",
]
