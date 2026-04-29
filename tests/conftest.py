"""Pytest-Setup: Fonts registrieren bevor Komponenten-Tests laufen."""

from __future__ import annotations

from mn_design_system.fonts import register_all_fonts

# Einmalig beim Test-Modul-Import registrieren (idempotent).
register_all_fonts()
