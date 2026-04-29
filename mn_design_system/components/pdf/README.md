# PDF-Komponenten (ReportLab)

Schicht 3 des MN PKA Design-Systems: Python-ReportLab-Implementierungen der Komponenten-Patterns.

## Verfuegbare Komponenten (v0.2.0)

| Funktion | Pattern-Spec | Output |
|---|---|---|
| `build_sparkline(input)` | `_patterns/sparkline.md` | `Drawing` mit `PolyLine` |
| `build_wetter_strip(input)` | `_patterns/wetter_strip.md` | `list[Flowable]` (Table + optional Summary) |
| `build_kpi_card(input)` | `_patterns/kpi_card.md` | `list[Flowable]` (5 Items: label, value, change, sparkline, caption) |

Alle Funktionen akzeptieren ihr zugehoeriges Pydantic-Input-Modell aus
`mn_design_system.components._patterns.contracts`.

## Setup beim Konsumenten

```python
from mn_design_system.fonts import register_all_fonts
register_all_fonts()  # einmal beim App-Start

from mn_design_system.components._patterns.contracts import (
    SparklineInput, KpiCardInput, WetterDay, WetterStripInput, WetterCategory,
)
from mn_design_system.components.pdf import (
    build_sparkline, build_wetter_strip, build_kpi_card,
)
```

## Beispiele

### Sparkline

```python
from reportlab.lib.units import mm

drawing = build_sparkline(SparklineInput(
    values=[100, 102, 98, 105, 110, 108],
    width=28 * mm,
    height=8 * mm,
))
story.append(drawing)
```

### KPI-Karte

```python
flowables = build_kpi_card(KpiCardInput(
    label="DAX",
    value="22.450,12",
    change_pct=1.25,
    sparkline_values=[22000, 22100, 22300, 22450],
    caption="Stand: Vortag-Schluss",
))
# flowables ist list[Flowable] — z.B. in Tabellen-Cell packen
```

### Wetter-Strip

```python
days = [
    WetterDay(header_label="Heute", category=WetterCategory.SONNIG,
              temp_min_c=12, temp_max_c=22, precip_pct=10),
    WetterDay(header_label="Mi", category=WetterCategory.HEITER,
              temp_min_c=10, temp_max_c=19, precip_pct=30),
    WetterDay(header_label="Do", category=WetterCategory.REGEN,
              temp_min_c=8, temp_max_c=14, precip_pct=80),
]
flowables = build_wetter_strip(WetterStripInput(
    days=days, location="Nuernberg",
    summary_text="Wechselhaft mit Aprilwetter-Charakter."
))
story.extend(flowables)
```

## Style-Konvention

Komponenten bauen ihre Styles **intern** aus Tokens (kein Style-Override-API).
Tokens sind die einzige Tuningstelle.

Schriftgroessen pro Komponente sind im Pattern-Spec dokumentiert. Fonts sind
hartkodiert auf Stack A (Geist + SourceSerif + Phosphor) — Stack-Wechsel
ist Welle E+ Aufgabe.

## Test-Konvention

Jede Komponente hat TDD-Tests in `tests/components/pdf/test_<komponente>.py`:
- Pydantic-Contract-Validation (positive + negative Cases)
- Build-Output-Struktur (Flowables-Anzahl, Typen)
- Visuelle Verhaltens-Pruefungen wo moeglich

Vor Test-Run muessen Fonts registriert sein — `tests/conftest.py` macht das
einmalig per Test-Session.

## Bezug

- Spec: `claudeAI/docs/superpowers/specs/2026-04-29-mn-design-system-v3-konsolidierung-design.md`
- Welle B: PDF-Implementierungen (diese Komponenten)
- Welle E+: Web/LaTeX-Pendants
