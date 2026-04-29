"""Pattern-Specs: renderer-agnostische Definitionen der Komponenten.

Jedes Pattern besteht aus:
- {pattern_name}.md — Anatomie, Tokens, Varianten, Verhalten (menschlich lesbar)
- contracts.py    — Pydantic-Modelle fuer API-Inputs (maschinen-lesbar)

Implementierungen pro Renderer (pdf/, web/, latex/) muessen die jeweiligen
Pydantic-Contracts akzeptieren.
"""

from mn_design_system.components._patterns.contracts import (
    KpiCardInput,
    KpiTrendDirection,
    SparklineInput,
    WetterCategory,
    WetterDay,
    WetterStripInput,
)

__all__ = [
    "KpiCardInput",
    "KpiTrendDirection",
    "SparklineInput",
    "WetterCategory",
    "WetterDay",
    "WetterStripInput",
]
