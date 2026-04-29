"""PDF-Komponenten (ReportLab) — Welle B v0.2.0.

Public-API:
    from mn_design_system.components.pdf import (
        build_sparkline,
        build_wetter_strip,
        build_kpi_card,
    )

Jede Funktion akzeptiert das zugehoerige Pydantic-Input-Modell aus
mn_design_system.components._patterns.contracts.
"""

from mn_design_system.components.pdf.kpi_card import build_kpi_card
from mn_design_system.components.pdf.sparkline import build_sparkline
from mn_design_system.components.pdf.wetter_strip import build_wetter_strip

__all__ = [
    "build_kpi_card",
    "build_sparkline",
    "build_wetter_strip",
]
