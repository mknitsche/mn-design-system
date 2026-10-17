# MN PKA Design-System — Architektur

> **Stand:** 2026-10-17 (v0.19.1). Beschreibt den Ist-Zustand; die Versions-Historie
> steht im [CHANGELOG](CHANGELOG.md), die Komponenten-Specs unter
> `mn_design_system/components/_patterns/`.
>
> Konsumenten-Rezepte (Konsumieren, neuen Token anlegen) stehen in der Anleitung
> im claudeAI-Repo: `docs/anleitungen/2026-04-29-ANL-012-token-konsumieren-richtig.md`.

---

## 1. Vier-Schichten-Modell

```
SCHICHT 4 — Anwendungen
  claudeAI-Briefings (PDF) · mkn-desk.com (Web) · Foto-Homepage, Paper (geplant)
  Konsumieren Komponenten oder den Loader, nicht die Token-Tabelle direkt.
        ↑ konsumiert
SCHICHT 3 — Komponenten
  _patterns/ (Markdown-Spec + Pydantic-Contract, frozen)
  pdf/ (ReportLab) · web/ (HTML + CSS + SVG/ECharts) · latex/ (vorgesehen)
        ↑ rendert auf Basis von
SCHICHT 2 — Typografie + Symbole
  Schriften unter mn_design_system/fonts/ (Geist, Source Serif 4, JetBrains Mono,
  STIX Two, Phosphor; dazu Noto Sans Symbols 2 fuer Symbole),
  Web-Schriftdateien (woff2) unter fonts/web/
        ↑ verweist auf Schluessel aus
SCHICHT 1 — Tokens (SSoT)
  tokens/*.json → Style Dictionary v4 → mn_design_system/tokens.py, dist/css, dist/json, dist/latex
```

Jede Schicht referenziert nur die direkt darunterliegende.

---

## 2. Pattern-First-Prinzip

Eine Komponente wird zuerst renderer-frei definiert (Markdown-Spec plus Pydantic-Contract),
dann pro Ausgabeziel implementiert.

```
mn_design_system/components/
├── _patterns/    Specs (*.md) und Contracts: contracts.py (Pdf-/Web-Komponenten),
│                 chat_contracts.py (Twin-Chat), _zahl.py / _verlauf.py (gemeinsame Helfer)
├── pdf/          ReportLab: kpi_card, sparkline, wetter_strip
├── web/          HTML/CSS/SVG: Komponenten-Familie, siehe § 5
└── latex/        vorgesehen, noch ohne Komponenten (siehe § 6)
```

Jede Komponente nimmt genau einen `*Input`-Typ. `frozen=True` verhindert Seiteneffekte,
`extra=forbid` laesst Tippfehler laut brechen. Gleiche Daten, gleicher Vertrag, je Renderer
eine Ausgabe. Nicht jede Komponente hat jeden Renderer: Zeitraum-Leiste, Verlauf-Chart und
alle Seiten-/Chat-Bausteine gibt es nur fuer Web.

---

## 3. Tokens

Quellen unter `tokens/` (Style Dictionary v4 baut daraus eine flache Lookup-Tabelle):

| Datei | Inhalt |
|---|---|
| `colors.json` | Farbpalette: Grau-/Indigo-Skala, Status-, Viz-, Kategorie- und Diagramm-Farben, Tier-Farben `color.tier.<tier>.*` |
| `typography.json` | `font.family.*` (inkl. Schnitte wie `sans-bold`), `font.size`, `font.leading`, `font.weight`, `font.tracking`, `font.hyphenation` |
| `spacing.json` | `space.*` (Abstands-Skala) |
| `radii.json` | `radius.*` |
| `strokes.json` | `stroke.*` (Linienstaerken) und `shadow.*` |
| `stack.json` | Schrift-Stack: Stack A (Geist + Source Serif 4 Italic) |
| `web.json` | Web-Schicht: `web.text`, `web.leading`, `web.font`, `web.stroke`, `web.color`, `web.layout`, `web.touch-target` |
| `families/indigo.json` | Familien-Definition der Indigo-Skala |

Tier-Tokens vorhanden fuer: bibliothek, atelier, kabinett, start, observatorium, archiv.

---

## 4. Web-Tiers

`WebTier` (in `_patterns/contracts.py`) benennt die Bereiche von mkn-desk.com und mappt
auf `color.tier.<tier>.*`: **bibliothek, atelier, kabinett, start, observatorium, archiv**.
`archiv` hat in 0.19.0 den Tier `magazin` abgeloest (gleiche Farbwerte, eigene Referenz auf die
Grau-Skala); 0.19.1 hat `magazin` samt Tokens und Fallbacks entfernt.

---

## 5. Web-Komponenten (`components/web/`)

| Modul | Zweck |
|---|---|
| `foundation` | Globale responsive Schicht (Media-Queries an den Breakpoints `web.layout.bp-*`), die Style Dictionary nicht erzeugen kann |
| `masthead` | Editorialer Seitenkopf: Identitaet (Wortmarke, Datum) und Tier-Navigation |
| `sub_nav` | Auswahl-Navigation innerhalb eines Tiers (Reiter) |
| `back_link` | Die eine Zurueck-Zeile unterhalb einer Reiterseite (nur interner Pfad) |
| `page_header` | Seitenkopf mit H1 und optionalem Lead |
| `footer` | Einzeilige Fusszeile mit Identitaets-Segmenten und Rechtslinks |
| `content_card` | Inhalts-Karte und Card-Grid, optional verlinkt und tier-getoent |
| `tier_chip` | Kleines tier-getoentes Etikett |
| `empty_state` | Ruhiger Leer-Zustand |
| `kpi_card` | Kennzahl-Karte (Wert, Veraenderung, Sparkline) |
| `sparkline` | Kleines Verlaufs-SVG |
| `wetter_strip` | Wetter-Tabelle mit Phosphor-Icons |
| `zeitraum_leiste` | Segment-Leiste aus Links (`?tage=30\|90\|365`), ohne Skript |
| `verlauf_chart` | Zeitreihen-Diagramm auf Apache ECharts: `verlauf_chart_option()` liefert die Option als reines JSON, das Rendern uebernimmt die vendorte Bibliothek |
| `chat_composer`, `chat_stream`, `status_banner`, `stream_cursor` | Bausteine des Twin-Chats (`/kabinett/chat`); Contracts in `chat_contracts.py`, Nachrichten werden clientseitig eingehaengt |

ECharts 6.1.0 liegt im Paket (`mn_design_system/vendor/echarts/`, Pin und Hash in
`VENDOR.json`, Lizenztexte daneben); kein CDN, kein Netz beim Seitenbau. Alle
Web-Komponenten stylen ueber `var(--…)` mit Rueckfall auf den Token-Wert.

---

## 6. PDF und LaTeX

- **PDF** (`components/pdf/`): ReportLab-Implementierungen von kpi_card, sparkline und
  wetter_strip. Produktiv, Konsument ist claudeAI (Briefings, Reports).
- **LaTeX** (`components/latex/`): vorgesehen, **noch ohne Komponenten**; das Paket ist ein
  leerer Platzhalter. Heute gibt es nur die Token-Ausgabe `dist/latex/tokens.tex`
  (`\def`-Macros). Komponenten kommen mit dem ersten LaTeX-Konsumenten (Paper).

---

## 7. Build-Pipeline

```
tokens/*.json
    │  npm run build  (Style Dictionary v4, build.js)
    ▼
mn_design_system/tokens.py   Python-Lookup, im Package
dist/css/tokens.css          Web
dist/json/tokens.json        flach, dotted keys
dist/latex/tokens.tex        \def-Macros
```

`dist/` wird committet (Konsumenten brauchen die Ausgaben); Python-Wheels nicht, sie
entstehen im Release-Workflow. `npm run validate` prueft WCAG-AA-Kontraste und
Pflicht-Tokens. `package.json` und `pyproject.toml` tragen dieselbe Version
(`tests/test_versionen_synchron.py`).

---

## 8. Konsumenten

| Konsument | Status | Bindung |
|---|---|---|
| **claudeAI** | aktiv (PDF, Briefings) | Python-Wheel aus dem Release |
| **mkn-desk.com** | aktiv (Web-Komponenten, Tiers) | Python-Wheel aus dem Release |
| **Foto-Homepage** (mkn-fotografie.de) | geplant | offen |
| **Paper / Newsletter** | geplant | offen |

---

## 9. Rechte und Änderungsweg

Das Repo ist oeffentlich lesbar, **source-available** unter PolyForm Strict 1.0.0
(nicht Open Source; Details im README, Abschnitt Rechte). Veraendern darf nur KT-1; seine
Terminal-Instanzen arbeiten ueber Branch → PR → Merge, `main` ist geschuetzt. Das
vollstaendige Modell steht im README, Abschnitt „Aenderungsweg".

---

## 10. Versionierung und Release

SemVer pre-1.0: `0.x.0` neue Komponente oder Token-Familie, `0.x.y` Bugfix, Doku, kleine
Token-Erweiterung; `1.0.0` erst mit zwei stabilen externen Konsumenten. Ein Release ist ein
Tag `vX.Y.Z` auf dem gemergten Commit; `release.yml` baut daraufhin das Wheel und haengt es
an das GitHub-Release.

---

## 11. Anti-Patterns

1. **Direkter Token-Import in Anwendungen** — Anwendungen konsumieren Komponenten oder
   den Loader. Ausnahme: Komponenten innerhalb dieses Packages.
2. **Renderer-Komponente ohne Pattern-Spec** — `pdf/foo.py` oder `web/foo.py` ohne
   `_patterns/foo.md` und Contract bricht das Pattern-First-Prinzip.
3. **Hartkodierte Werte in Tests** — Tokens ueber `mn_design_system.tokens.get` lesen.
4. **Logos im Repo** — proprietaer, gehoeren nicht in den oeffentlichen Teil (siehe NOTICE).
5. **Build-Output ohne Quelle** — `npm run build` ist deterministisch; ein Commit, der nur
   `tokens.py` oder `dist/` aendert, ohne dass sich `tokens/` aendert, ist verdaechtig.

---

## Verwandte Dokumente

- **CHANGELOG.md** — Versions-Historie
- **README.md** — Schnellstart, Stack, Rechte, Aenderungsweg
- **CITATIONS.md** — Schrift- und Symbol-Lizenzen
- **claudeAI** — `system/referenz/background-notes/design-system.md` (Werdegang),
  `docs/anleitungen/2026-04-29-ANL-012-token-konsumieren-richtig.md` (Konsumieren)
