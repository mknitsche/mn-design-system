# Changelog

Alle nennenswerten Aenderungen am MN PKA Design-System.

Format: [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) · SemVer pre-1.0
(Solo-Maintainer-Modus): `0.x.0` = neue Komponente/Token-Familie, `0.x.y` = Bugfix
oder Doku.

---

## [0.4.0] — 2026-04-30

### Added
- **GitHub Actions Workflow `.github/workflows/release.yml`** — Tag-getriggert (`v*.*.*`),
  baut Wheel via `python -m build --wheel` und published als GitHub Release Asset.
  Nutzt `GITHUB_TOKEN` (out-of-the-box, kein zusaetzliches Secret).
- **GitHub Actions Workflow `.github/workflows/build-tokens.yml`** — bei Push auf
  `tokens/**`: prueft ob `mn_design_system/tokens.py` synchron mit Style-Dictionary-Build
  ist. Fail-on-diff (kein Auto-Commit, klare Disziplin fuer Solo-Maintainer).
- Erste **versionierte Wheel-Distribution** als GitHub Release Asset: konsumierbar via
  `mn-design-system @ git+https://github.com/mknitsche/mn-design-system.git@v0.4.0`
  oder direkter Wheel-URL.

### Notes
- **Welle F (S239 Entscheidung):** Distributions-Schicht B aktiviert. claudeAI bindet
  ab v0.4.0 via Wheel-URL statt Submodul (`pip install -e ./system/design-system/`).
- **Distributions-Wahl:** GitHub Release Asset statt PyPI. Begruendung: KT-1 will
  gezielt einzelnen Personen zeigen statt suchindexiert publizieren. PyPI bleibt
  spaeter migrationsfaehig (release.yml einmal um `pypa/gh-action-pypi-publish`
  ergaenzen).
- Welle E (Style-Dictionary Custom-Format) bleibt verschoben — Spec-Annex § Welle E.

---

## [0.3.0] — 2026-04-29

### Added
- `ARCHITECTURE.md` — 4-Schichten-Modell + Pattern-First-Prinzip + Konsumenten-Liste +
  Distributions-Schichten + Anti-Patterns
- `CHANGELOG.md` (diese Datei)

### Changed
- `README.md` erweitert um Python-Setup, Versionierungs-Politik, Multi-KI-Edit-Workflow,
  Distributions-Schichten, vollstaendige Tag-Historie

### Notes
- Welle D.4-D.6 (GitHub Action `release.yml`, `build-tokens.yml`, claudeAI-pyproject
  GitHub-Packages-Dependency) sind **vorbereitet, aber YAGNI-deferred** bis erster
  externer Konsument live ist (Foto-Homepage / Paper). Begruendung: Gemini-Review v1.1.

---

## [0.2.1] — 2026-04-29

### Added
- **12 neue Tokens** in `tokens/colors.json`:
  - `color.status.urgent` (#e65100)
  - `color.status.error-bg` (#ffebee), `warning-bg` (#fff3e0)
  - `color.status.error-tint` (#fff8f7), `warning-tint` (#fffaf5), `info-tint` (#f5f8ff)
  - `color.viz.muted` (#b0bec5), `success-soft` (#90caf9), `neutral-soft` (#e0e0e0)
  - `color.viz.dark-navy` (#1a237e), `medium-blue` (#283593)
  - `color.grey.50` (#f5f5f5), `grey.150` (#eeeeee), `grey.550` (#666666),
    `grey.600` (#999999)

### Changed
- 28 Hex-Migrationen ueber 7 Skill-Module im claudeAI-Konsumenten:
  `system_doc_v2.py`, `pdf_projekt_status.py`, `viz_generate.py`, `handbuch_pdf.py`,
  `preview_logos.py`, `pdf_utils.py`, `renderer_v2.py`
- Audit-Script `scripts/audit_hardcoded_design_values.py` (im claudeAI-Repo) gruen:
  0/330 Treffer
- Konsistenz-Beleg: `#2e7d32` (success-Gruen) war 8x verstreut in claudeAI, ist jetzt
  ein einziger Token

---

## [0.2.0] — 2026-04-29

### Added
- **Pattern-First-Architektur** unter `mn_design_system/components/`:
  - `_patterns/contracts.py` — Pydantic-Modelle (`frozen=True, extra=forbid`):
    `SparklineInput`, `KpiCardInput`, `WetterStripInput`, `WetterDay`,
    `KpiTrendDirection`, `WetterCategory`
  - `_patterns/sparkline.md`, `kpi_card.md`, `wetter_strip.md` — renderer-agnostische Specs
- **PDF-Implementierungen** unter `mn_design_system/components/pdf/`:
  - `sparkline.py` — `build_sparkline(input)` mit adaptiver Skala (±10% Default,
    ±5% Min, auto-widening)
  - `kpi_card.py` — `build_kpi_card(input)` mit 5 Flowables (label/value/change/
    sparkline/caption)
  - `wetter_strip.py` — `build_wetter_strip(input)` mit Phosphor-Icon-Mapping fuer
    8 Wetter-Kategorien
- Multi-Renderer-Stubs `components/web/`, `components/latex/`
- 50 Component-Tests (`tests/components/`) — alle gruen

### Changed
- Token-Build-Output `python` von `dist/python/tokens.py` nach
  `mn_design_system/tokens.py` verlegt — `pip install -e` greift jetzt direkt
  ohne Pfad-Hack zu

---

## [0.1.0] — 2026-04-29

### Added
- **Initialfassung** als Public-Repo unter `github.com/mknitsche/mn-design-system`
- **MIT-Lizenz** (Tokens + Code) · OFL 1.1 (Schriften) · MIT (Phosphor)
- **Token-Quellen** (`tokens/`):
  - `colors.json` — Indigo-Familie 50–900, Status-Farben, Brand, Light/Dark-Themes
  - `type.json` — Schrift-Rollen + Skalen (Body 10pt/15.5pt mit Hyphenation)
  - `space.json`, `radii.json`, `stroke.json` — 4pt-Skala, Card-/Tag-Radii, Divider-/
    Card-Border-Strokes
- **Style Dictionary v4** mit Build-Targets:
  - `dist/css/tokens.css` — CSS Custom Properties (Web)
  - `dist/json/tokens.json` — flat dotted keys
  - `dist/latex/tokens.tex` — `\def`-Macros
- **Python-Package** `mn_design_system`:
  - `tokens.py` — Build-Output direkt im Package
  - `fonts/__init__.py::register_all_fonts()` — 35 ReportLab-Font-Registrierungen
    (Geist, Source Serif, JetBrains Mono, STIX, Phosphor, Inter, Noto Sans + Helvetica/
    Arial-Aliase)
  - Font-Pfad-Resolver via `importlib.resources` (funktioniert mit editable + wheel install)
- **Token-Validierung** (`scripts/validate-tokens.js`):
  - WCAG-AA-Kontraste fuer alle Body/Header-Farben (Light + Dark)
  - Color-Token Hex-Format
  - Required-Tokens vorhanden
- GitHub Action `validate-tokens.yml` auf Push
- `pyproject.toml` v0.1.0 mit `reportlab>=4.0`, `pydantic>=2.0` als Dependencies
- `setuptools.package-data` fuer Font-Dateien

---

## Vor v0.1.0

Vorlaeufer-Phasen lebten direkt im claudeAI-Repo unter `system/lib/design_system.py`
(Stack A-Wahl, Token-Definition, Helvetica-Migration). Der Werdegang ist als Narrativ
in `claudeAI/system/referenz/background-notes/design-system.md` dokumentiert.

---

[0.3.0]: https://github.com/mknitsche/mn-design-system/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/mknitsche/mn-design-system/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mknitsche/mn-design-system/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mknitsche/mn-design-system/releases/tag/v0.1.0
