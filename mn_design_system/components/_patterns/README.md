# Pattern-Specs (Schicht 3 — renderer-agnostisch)

Pro Komponente eine Markdown-Spec (menschen-lesbar) plus Pydantic-Modelle in
`contracts.py` (maschinen-lesbar).

## Warum Pattern-First?

Das Design-System soll mehrere Renderer bedienen koennen — heute PDF (ReportLab),
morgen Web (HTML/CSS/React), spaeter LaTeX. Wenn Komponenten direkt als
ReportLab-Code gebaut wuerden, koennten andere Renderer nichts mit ihnen anfangen.

**Loesung:** jede Komponente ist erst ein _Pattern_ (was ist sie, was sind ihre
Inputs, wie verhaelt sie sich). Pro Renderer-Sprache wird das Pattern dann
implementiert. Pydantic-Contracts erzwingen API-Konsistenz zwischen
Implementierungen.

## Verfuegbare Patterns (v0.2.0)

| Pattern | Spec | Pydantic-Input | PDF-Impl |
|---|---|---|---|
| Sparkline | `sparkline.md` | `SparklineInput` | `pdf/sparkline.py` |
| Wetter-Strip | `wetter_strip.md` | `WetterStripInput`, `WetterDay` | `pdf/wetter_strip.py` |
| KPI-Card | `kpi_card.md` | `KpiCardInput`, `KpiTrendDirection` | `pdf/kpi_card.py` |

## Workflow fuer neue Patterns

1. Markdown-Spec schreiben (`<pattern>.md`): Anatomie, API, Tokens, Varianten, Verhalten
2. Pydantic-Modell ergaenzen (`contracts.py`)
3. Mindestens eine Renderer-Implementierung (`pdf/<pattern>.py`)
4. TDD-Tests gegen Pattern-Spec (`tests/components/pdf/test_<pattern>.py`)
5. README aktualisieren (diese Datei + `pdf/README.md`)
6. SemVer-Bump + Tag

## Renderer-Implementierungen

- `pdf/` — ReportLab (Welle B v0.2.0)
- `web/` — HTML/CSS/React (geplant, wenn Foto-Homepage Code bekommt)
- `latex/` — LaTeX/TikZ (geplant, wenn Paper-Workflow startet)

Jede Renderer-Implementierung **muss** das zugehoerige Pydantic-Modell als Input
akzeptieren. So sind APIs cross-renderer konsistent.

## Bezug

Pattern-First-Architektur ist Antwort auf Gemini-Review (v1.0 -> v1.1, Befund 1):
"Vermischung Design-System ↔ Implementierungs-Bibliothek". Specs in `claudeAI/docs/superpowers/specs/2026-04-29-mn-design-system-v3-konsolidierung-design.md`.
