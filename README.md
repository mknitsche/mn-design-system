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

Details: **`ARCHITECTURE.md`** · Spec im claudeAI-Repo: `docs/superpowers/specs/2026-04-29-mn-design-system-v3-konsolidierung-design.md`.

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

## Rechte

> **In short (English):** This repository is public so that it can be **read and
> used** — not so that it can be changed. It is not open source: the licence
> withholds the right to modify or redistribute. Bug reports are welcome; pull
> requests are not accepted. Bundled fonts keep their own (open) licences.

Dieses Repository ist **oeffentlich lesbar, aber nicht offen zur Mitarbeit**.
Das ist eine bewusste Unterscheidung:

| | |
|---|---|
| **Lesen** | erlaubt — dafuer ist es oeffentlich |
| **Nutzen** | fuer nicht-kommerzielle Zwecke; PolyForm Strict deckt kommerzielle Nutzung durch Dritte NICHT (fragen kostet nichts) |
| **Weitergeben** | nicht erlaubt — auch nicht unveraendert. Ein **Verweis auf dieses Repository** ist der richtige Weg; es als Submodul, Vendor-Kopie oder Spiegel in ein eigenes veroeffentlichtes Projekt aufzunehmen, ist es nicht |
| **Veraendern** | nur durch den Rechteinhaber |
| **Beitraege** | Issues ja, Pull Requests nein (siehe `CONTRIBUTING.md`) |

Gestaltung ist hier kein Sammelergebnis. Farbe, Typografie, Rhythmus und Ton
sind Entscheidungen einer Person und bleiben es — deshalb ist dies
**source-available**, nicht Open Source. Jede OSI-Lizenz (MIT, Apache, GPL)
raeumt ausdruecklich das Recht zur Veraenderung ein; genau das ist hier nicht
gewollt.

- **Design-System (Tokens, Komponenten, Doku, Build-Skripte)**:
  PolyForm Strict 1.0.0 — siehe `LICENSE`
- **Schriften**: SIL OFL 1.1 (Geist, Source Serif 4, Source Sans 3, STIX) und
  Apache 2.0 (JetBrains Mono) — **behalten ihre eigenen, offenen Lizenzen**;
  `LICENSE` schraenkt sie nicht ein
- **Symbole**: MIT (Phosphor Icons)
- **Logos** (mkn-fotografie / PKA): proprietaer, keine Markenrechte eingeraeumt
  — NICHT in diesem Repo, siehe `NOTICE`

Quellenangaben + Lizenz-Texte: `CITATIONS.md` · Marken und Fremdbestandteile:
`NOTICE` · Sicherheitsmeldungen: `SECURITY.md`.

Etwas Eigenes daraus machen? Das ist eine Frage, keine Sperre — fragen kostet
nichts.

## Python-Setup (claudeAI als Konsument)

Das Repo liefert ein installierbares Python-Package `mn_design_system`. Konsumenten
binden es als Submodul ein und installieren editable:

```bash
# Im Konsumenten-Repo (z.B. claudeAI)
git submodule add https://github.com/mknitsche/mn-design-system.git system/design-system
.venv/bin/pip install -e ./system/design-system/
```

Konsumieren:

```python
from mn_design_system.fonts import register_all_fonts
from mn_design_system.tokens import get

register_all_fonts()                  # ReportLab-Fonts registrieren
text_color = get("color.light.text")  # "#1e1b4b"
```

Komplette Komponenten:

```python
from mn_design_system.components.pdf.kpi_card import build_kpi_card
from mn_design_system.components._patterns.contracts import KpiCardInput

flowables = build_kpi_card(KpiCardInput(
    label="DAX",
    value="18.234",
    change_pct=1.23,
    sparkline_values=[100, 101, 99, 102, 105],
    caption="Stand 09:00",
))
```

## Versionierungs-Politik

**SemVer pre-1.0** (Solo-Maintainer-Modus):

- `0.x.0` — neue Komponente, neue Token-Familie, ARCHITECTURE-Aenderung
- `0.x.y` — Bugfix, Doku, kleine Token-Erweiterung
- `1.0.0` — erst wenn zwei stabile externe Konsumenten leben (Foto-Homepage + Paper o.ae.)

Tags werden im Submodul gesetzt. Konsumenten ziehen den Submodul-Pointer im selben
Sprint per Commit nach. Drift-Schutz: Pre-Commit-Hook im Konsumenten-Repo warnt
bei alten Pointern.

## Konsumenten-Liste

| Konsument | Status | Bindung |
|---|---|---|
| **claudeAI** | Aktiv (wesentlichster Konsument) | Submodul + `pip install -e` |
| **Foto-Homepage** (mkn-fotografie.de) | Geplant (PRJ-9) | TBD |
| **KI-News** | Aktiv (innerhalb claudeAI) | Indirekt |
| **Paper / Newsletter** | Geplant | TBD |

## Multi-KI-Edit-Workflow

Das Repo ist **public** — lesbar, aber source-available und nicht veraenderbar
(siehe Abschnitt Rechte). Fuer KT-1s eigene Werkzeuge gilt diese Schranke nicht:
sie arbeiten in seinem Namen und duerfen direkt am Token-Set arbeiten:

- **Claude Design** (browser) — Token-/Komponenten-Edit ohne IDE-Roundtrip
- **Codex Web** — gleiche Idee, andere KI
- **Cursor / GitHub Copilot** — IDE-Integration mit Repo-Kontext
- **Terminal-Sessions** — claudeAI-Hauptsession, Worktrees

Jede dieser KI-Quellen committet auf `main`, claudeAI-Konsumenten ziehen den
Submodul-Pointer nach. Konsistenz-Schutz: SemVer-Tags + Pre-Commit-Drift-Hook.

## Distributions-Schichten

Heute aktiv: **Submodul-Live-Edit** (siehe Python-Setup oben).

Zwei weitere Schichten **vorbereitet, YAGNI-deferred** bis erster externer Konsument:

- **GitHub Packages** — versionierte Wheel-Distribution fuer Konsumenten ohne Submodul-Setup
- **PyPI public** — oeffentliche Paket-Distribution falls Drittnutzer auftreten (die Lizenz bleibt source-available, siehe Abschnitt Rechte)

Aktivierung pro Schicht: GitHub Action `release.yml` (Tag-Trigger) liefert Wheel.

## Verwandte Dokumente (im claudeAI-Repo)

- ADR-008 Fundament-Entscheidung
- Spec v3 — `docs/superpowers/specs/2026-04-29-mn-design-system-v3-konsolidierung-design.md`
- BACKGROUND-NOTES — `system/referenz/background-notes/design-system.md` (Werdegang)
- Konsum-Anleitung — `docs/anleitungen/2026-04-29-ANL-012-token-konsumieren-richtig.md`

## Status

| Tag | Datum | Inhalt |
|---|---|---|
| `v0.1.0` | 2026-04-29 | Repo + Tokens + Style Dictionary + Python-Package + 35 Fonts |
| `v0.2.0` | 2026-04-29 | Pattern-First-Architektur + 3 PDF-Komponenten (Sparkline/KPI/Wetter-Strip) |
| `v0.2.1` | 2026-04-29 | 12 neue Tokens (Status-bg/-tint, Viz-Familie, Grey-Erweiterung) + Audit-Script |
| `v0.3.0` | 2026-04-29 | Doku-Architektur (ARCHITECTURE + erweitertes README + CHANGELOG) |

Phase H (Foto-Homepage) und Welle D.4-D.6 (GitHub-Packages-Distribution) sind
**vorbereitet, aber YAGNI-deferred** bis erster externer Konsument startet.

---

Built with ❤️ in Nürnberg.
