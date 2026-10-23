"""LaTeX-Druckschicht des Design-Systems (v0.21.0).

Public-API:
    from mn_design_system.latex import LATEX_DIR, STY
    # TEXINPUTS="<LATEX_DIR>//:" und \\def\\mndsfontdir{<mn_design_system.fonts.FONT_DIR>}
    # vor \\usepackage{mn-design}

``mn-design.sty`` erzeugt ``build.js`` (Format ``latex/sty``) aus den Tokens: jede Farbe als
xcolor-Farbe, die semantischen Dokumentfarben und die Schriften per Pfad aus dem Paket — nie
ueber Fontconfig, denn unter ``fonts/web/`` liegen ``.woff2``-Dateien, die XeTeX nicht einbetten kann.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

LATEX_DIR: Path = Path(str(files("mn_design_system") / "latex"))
STY: Path = LATEX_DIR / "mn-design.sty"

__all__ = ["LATEX_DIR", "STY"]
