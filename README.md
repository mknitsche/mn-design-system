# MN PKA Design-System — "Radical Clarity"

> Eine einheitliche visuelle Grammatik für alle Outputs des Personal Knowledge Assistant.

## Was ist das

Ein **token-basiertes Design-System** für Multi-Plattform-Outputs:

- **Briefings, Reports, KI-News** (PDF via ReportLab)
- **Wissenschaftliche Paper** (LaTeX)
- **Web-App + Foto-Homepage** (HTML/CSS, später React)
- **Newsletter, private Texte**

Eine Token-Definition, vier Renderer-Targets, kein Refactoring bei Schrift- oder Farb-Wechsel.

## Schnellstart

```bash
git clone https://github.com/mknitsche/mn-design-system.git
cd mn-design-system
npm install
npm run build
```

Generiert:

- `dist/css/tokens.css` — CSS Custom Properties (Web)
- `dist/python/tokens.py` — Python-Dict (ReportLab)
- `dist/json/tokens.json` — flach, dotted keys
- `dist/latex/tokens.tex` — `\def`-Macros (LaTeX)

## Architektur

Vier Schichten:

```
SCHICHT 4 — Anwendungen (Briefing, Web-App, Foto-Homepage, Paper, ...)
SCHICHT 3 — Komponenten (Brand-Header, KPI-Karte, Wetter-Strip, ...)
SCHICHT 2 — Typography + Symbole (Geist, Source Serif, JetBrains Mono, STIX, Phosphor)
SCHICHT 1 — Tokens (Color, Type, Spacing, Radii, Strokes — SSoT)
```

Details: `ARCHITECTURE.md` (kommt bald) · Spec im claudeAI-Repo: `docs/superpowers/specs/2026-04-29-mn-design-system-v2-design.md`.

## Stack

**Default Stack A** — KT-1's Wahl 2026-04-29:
- Body: **Geist** (Vercel · OFL 1.1)
- Italic Editorial: **Source Serif 4 Italic** (Adobe · OFL 1.1)
- Italic UI: **Geist Medium** (kein Sans/Serif-Bruch in Tabellen/Status)
- Mono: **JetBrains Mono** (Apache 2.0)
- Math: **STIX Two Math** (OFL 1.1)
- Symbole: **Phosphor Icons** (MIT)

**Stack D** als Alternative (Source Sans 3) bleibt im Repo. Wechsel via `MN_PKA_STACK=D npm run build`.

## Token-Validierung (CI)

`npm run validate` prüft:

1. WCAG-AA-Kontraste für alle Body/Header-Farben (Light + Dark)
2. Color-Token Hex-Format
3. Required-Tokens vorhanden

Github Action läuft auf jeden Push — siehe `.github/workflows/validate-tokens.yml`.

## Hyphenation

Token `font.hyphenation.enabled` (Default `true`) aktiviert deutsche Silbentrennung in allen Renderern:

- Python/PDF: `pyphen` mit `lang=de_DE`
- Web: CSS `hyphens: auto` mit `<html lang="de">`
- LaTeX: `\usepackage[ngerman]{babel}`

Löst das Blocksatz-Lückenproblem bei Body-Größen ≥10pt.

## Lizenzen

- **Tokens + Code**: MIT (siehe `LICENSE`)
- **Schriften**: SIL OFL 1.1 (Geist, Source Serif 4, Source Sans 3, STIX) und Apache 2.0 (JetBrains Mono)
- **Symbole**: MIT (Phosphor Icons)
- **Logos** (mkn-fotografie / PKA): proprietär — NICHT in diesem Repo

Quellenangaben + Lizenz-Texte: `CITATIONS.md`.

## Verwandte Dokumente (im claudeAI-Repo)

- ADR-008 Fundament-Entscheidung
- Spec v2.1 (Detail-Spezifikation)
- BACKGROUND-NOTES `system/referenz/background-notes/design-system.md` (Werdegang)

## Status

- v0.1.0 — Initialfassung 2026-04-29 (S238)
- Phase A: Repo + Tokens + Style Dictionary ✓
- Phase B: claudeAI-Migration (laufend)
- Phase H: Foto-Homepage Smugmug-Ablöse (geplant)

---

Built with ❤️ in Nürnberg.
