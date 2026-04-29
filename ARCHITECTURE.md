# MN PKA Design-System — Architektur

> **Stand:** 2026-04-29 (v0.3.0) · S238 Welle D
>
> Dieses Dokument beschreibt das **architektonische Fundament** des Design-Systems —
> die vier Schichten, das Pattern-First-Prinzip und die Multi-Renderer-Targets.
> Versionsuebergreifende Rezepte (Konsumieren, neuen Token anlegen) stehen in der
> Konsumenten-Anleitung im claudeAI-Repo:
> `docs/anleitungen/2026-04-29-ANL-012-token-konsumieren-richtig.md`.

---

## 1. Vier-Schichten-Modell

```
┌─────────────────────────────────────────────────────────────────┐
│ SCHICHT 4 — Anwendungen                                         │
│   claudeAI-Briefings · Foto-Homepage · KI-News · Paper · Web    │
│   Ein Konsument pro Anwendung, kein direkter Token-Zugriff      │
└─────────────────────────────────────────────────────────────────┘
                              ↑ konsumiert
┌─────────────────────────────────────────────────────────────────┐
│ SCHICHT 3 — Komponenten                                         │
│   _patterns/ (Markdown-Spec + Pydantic-Contract, frozen)        │
│   pdf/      web/      latex/                                    │
│   build_kpi_card / build_sparkline / build_wetter_strip / ...   │
└─────────────────────────────────────────────────────────────────┘
                              ↑ rendert auf Basis von
┌─────────────────────────────────────────────────────────────────┐
│ SCHICHT 2 — Typografie + Symbole                                │
│   register_all_fonts() (Geist, Source Serif, JetBrainsMono,     │
│   STIX Two Math, Phosphor Icons)                                │
│   Single-Entry-Point ueber importlib.resources                  │
└─────────────────────────────────────────────────────────────────┘
                              ↑ verweist auf Schluessel aus
┌─────────────────────────────────────────────────────────────────┐
│ SCHICHT 1 — Tokens (SSoT)                                       │
│   tokens/colors.json · tokens/type.json · tokens/space.json ... │
│   Style Dictionary v4 → mn_design_system/tokens.py              │
│   color.indigo.50 / color.status.success / type.body.size ...   │
└─────────────────────────────────────────────────────────────────┘
```

Jede Schicht referenziert nur die direkt darunterliegende. Anwendungen importieren
**nicht** aus Schicht 1 — sie konsumieren Komponenten oder den Loader.

---

## 2. Pattern-First-Prinzip (seit v0.2.0)

Komponenten werden zuerst **renderer-agnostisch** definiert, dann pro Target
implementiert.

```
mn_design_system/components/
├── _patterns/                     ← Schicht 3 SSoT (renderer-frei)
│   ├── contracts.py               ← Pydantic-Models, frozen=True, extra=forbid
│   ├── kpi_card.md                ← textuelle Spec (Inputs/Outputs/Verhalten)
│   ├── sparkline.md
│   └── wetter_strip.md
├── pdf/                           ← ReportLab-Implementierung
│   ├── kpi_card.py                ← build_kpi_card(input: KpiCardInput)
│   ├── sparkline.py
│   └── wetter_strip.py
├── web/                           ← (Stub) HTML/CSS-Implementierung
└── latex/                         ← (Stub) LaTeX-Implementierung
```

**Pydantic-Contract als Vertrag.** Jede Komponente nimmt genau einen `*Input`-Typ.
`frozen=True` verhindert Side-Effects, `extra=forbid` verhindert Tippfehler
("subline" statt "caption" bricht laut, nicht still).

Beispiel:

```python
class KpiCardInput(BaseModel):
    model_config = {"extra": "forbid", "frozen": True}
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)
    change_pct: float | None = None
    sparkline_values: list[float] | None = None
    caption: str | None = None
```

Renderer haben damit Identische Eingabe-Garantie ueber pdf/web/latex hinweg —
gleiche Daten, drei Outputs, ein Vertrag.

---

## 3. Token-Hierarchie

Style Dictionary v4 baut **flache Lookup-Tabelle** aus den hierarchischen JSONs.
Die Hierarchie dient der Pflege, nicht der Konsumation.

| JSON-Quelle | Beispiel-Schluessel | Zweck |
|---|---|---|
| `tokens/colors.json` | `color.indigo.600`, `color.status.success`, `color.viz.muted` | Farbpalette inkl. Status- und Viz-Familien |
| `tokens/type.json` | `type.body.size`, `type.h1.leading`, `font.hyphenation.enabled` | Schrift-Rollen + Skalen |
| `tokens/space.json` | `space.xs`, `space.gutter`, `space.section-gap` | Abstaende (4pt-Skala) |
| `tokens/radii.json` | `radius.card`, `radius.tag` | Eck-Radien |
| `tokens/stroke.json` | `stroke.divider`, `stroke.card-border` | Linien-Staerken |

**Token-Familien-Konvention** (Tailwind-inspiriert):
- Skala 50–950 fuer Farb-Familien (z.B. `color.indigo.50` bis `color.indigo.900`)
- Semantische Status-Familie: `color.status.{success,warning,urgent,error,info}` plus
  `-bg`/`-tint`-Varianten fuer Background-/Hervorhebungs-Layer
- Viz-Familie fuer Diagramme/Tabellen: `color.viz.{muted,success-soft,neutral-soft,
  dark-navy,medium-blue}` (separat von UI-Farben, weil andere Kontrast-Anforderungen)

---

## 4. Build-Pipeline

```
tokens/*.json
    │
    │  npm run build  (Style Dictionary v4)
    ▼
mn_design_system/tokens.py   ← In-Package, NICHT mehr in dist/python/
                               (seit Welle A v0.1.0 direkt im Python-Package)
dist/css/tokens.css          ← Web-Konsumenten
dist/json/tokens.json        ← flat, dotted keys (ML/Tools)
dist/latex/tokens.tex        ← \def-Macros
```

Begruendung fuer **In-Package-Output**: `pip install -e ./system/design-system/`
greift dann auf `mn_design_system/tokens.py` direkt zu, kein Pfad-Hack noetig.
`dist/` bleibt fuer Multi-Renderer-Konsumenten erhalten (Web/LaTeX).

---

## 5. Konsumenten-Liste

| Konsument | Status | Bindungs-Modus |
|---|---|---|
| **claudeAI** | Aktiv (wesentlichster Konsument) | Submodul + `pip install -e ./system/design-system/` |
| **Foto-Homepage** (mkn-fotografie.de) | Geplant (PRJ-9) | TBD: Submodul oder Sub-Repo-Ausschnitt |
| **KI-News** | Aktiv (innerhalb claudeAI) | Indirekt ueber claudeAI-Loader |
| **Wissenschaftliche Paper** | Geplant | TBD |
| **Newsletter / private Texte** | Geplant | TBD |

**Multi-KI-Edit-Faehigkeit**: Das Repo ist **public** (MIT-Lizenz, ohne Logos).
Damit koennen Claude Design Browser, Codex Web, Cursor und andere Tools direkt
im Token-Set arbeiten ohne IDE-Roundtrip. claudeAI bleibt privat (PII), die
Design-Schicht ist offen — bewusste Trennung.

---

## 6. Versionierungs-Politik

**SemVer pre-1.0** (Solo-Maintainer-Modus):

- `0.x.0` — Neue Komponente, neue Token-Familie, ARCHITECTURE-Aenderung
- `0.x.y` — Bugfix, Doku, kleine Token-Erweiterung
- `1.0.0` — Erst wenn Foto-Homepage als zweiter Konsument live ist und Paper-Konsument absehbar (zwei stabile Konsumenten = SemVer-Garantien lohnen)

**Tag-Disziplin im Submodul-Repo:**

```bash
cd system/design-system
git tag v0.3.0 -m "Welle D: Architektur-Doku"
git push origin main --tags
```

claudeAI-Pointer wird im selben Sprint per Commit nachgezogen:

```bash
cd /Users/mkn1972/claudeAI
git add system/design-system
git commit -m "chore(design-system): Submodul auf v0.3.0"
```

---

## 7. Distributions-Schichten

Heute: **eine Schicht aktiv** (Submodul-Live-Edit). Zwei weitere vorbereitet, YAGNI-deferred.

| Schicht | Zweck | Status |
|---|---|---|
| **Submodul (Live-Edit)** | Schnelle Iteration, Multi-KI-Edit, claudeAI greift direkt zu | **AKTIV** |
| **GitHub Packages (versioniert)** | Externe Konsumenten ohne Submodul-Setup, klare SemVer-Bindung | **VORBEREITET** (release.yml in Welle D YAGNI-deferred bis erster externer Konsument) |
| **PyPI public (langfristig)** | Open-Source-Distribution | **VAGUE** (nur wenn Drittnutzer auftreten) |

**Wann GitHub-Packages aktivieren?** Wenn der erste externe Konsument (Foto-Homepage,
Paper) startet. Dann release.yml + build-tokens.yml + claudeAI-pyproject-Dependency
nachziehen.

---

## 8. Anti-Patterns

1. **Direkter Token-Import in Anwendungen** — Anwendungen konsumieren Komponenten
   oder den Loader, nicht `mn_design_system.tokens.get` direkt. Ausnahme:
   Komponenten **innerhalb** dieses Packages (Symmetrie zur eigenen API).

2. **Renderer-spezifische Komponenten ohne Pattern-Spec** — `pdf/foo.py` ohne
   `_patterns/foo.md` + Contract bricht das Multi-Renderer-Versprechen.

3. **Hartkodierte Werte in Tests** — Tests muessen Tokens via `from
   mn_design_system.tokens import get` referenzieren, nicht Hex-Strings im Code.

4. **Logos im Repo** — proprietaer, gehoeren nicht in den Public-MIT-Bereich.
   Logo-Pfade sind im Konsumenten (claudeAI) gepflegt, nicht hier.

5. **Build-Output committen ohne Konsistenz-Check** — `npm run build` muss
   deterministisch sein (gleicher Token-Stand → gleicher Output). Commits, die
   nur `tokens.py` aendern ohne `tokens/colors.json`-Aenderung, sind verdaechtig.

---

## Verwandte Dokumente

- **CHANGELOG.md** — Versions-Historie pro Tag
- **README.md** — Schnellstart + Stack-Wahl
- **CITATIONS.md** — Schrift- und Symbol-Lizenzen
- **claudeAI BG-Note** — `system/referenz/background-notes/design-system.md` (Werdegang)
- **claudeAI Anleitung** — `docs/anleitungen/2026-04-29-ANL-012-token-konsumieren-richtig.md` (Konsumieren in claudeAI)
- **claudeAI Spec v3** — `docs/superpowers/specs/2026-04-29-mn-design-system-v3-konsolidierung-design.md`
