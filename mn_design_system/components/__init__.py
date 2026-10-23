"""MN PKA Design-System — Komponenten-Schicht (Schicht 3).

Pattern-First-Architektur:
- _patterns/    — renderer-agnostische Pattern-Specs (Markdown + Pydantic-Contracts)
- pdf/          — Python-ReportLab-Implementierungen (Welle B, S238)
- web/          — HTML/CSS/React (geplant, wenn Foto-Homepage Code bekommt)
- LaTeX: keine Komponenten hier — die eine LaTeX-Schicht ist mn_design_system/latex/ (mn-design.sty, v0.21.0)

Jede Komponente ist ein Pattern, das pro Renderer separat implementiert wird.
Tokens (Color, Spacing, Typography) sind die gemeinsame Basis.
"""

__all__: list[str] = []
