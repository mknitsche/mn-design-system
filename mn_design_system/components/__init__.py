"""MN PKA Design-System — Komponenten-Schicht (Schicht 3).

Pattern-First-Architektur:
- _patterns/    — renderer-agnostische Pattern-Specs (Markdown + Pydantic-Contracts)
- pdf/          — Python-ReportLab-Implementierungen (Welle B, S238)
- web/          — HTML/CSS/React (geplant, wenn Foto-Homepage Code bekommt)
- latex/        — LaTeX-Implementierungen (geplant, wenn Paper-Workflow startet)

Jede Komponente ist ein Pattern, das pro Renderer separat implementiert wird.
Tokens (Color, Spacing, Typography) sind die gemeinsame Basis.
"""

__all__: list[str] = []
