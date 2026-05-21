# Changelog

Alle nennenswerten Aenderungen am MN PKA Design-System.

Format: [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) · SemVer pre-1.0
(Solo-Maintainer-Modus): `0.x.0` = neue Komponente/Token-Familie, `0.x.y` = Bugfix
oder Doku.

---

## [0.10.0] — 2026-05-21

### Geaendert — Footer als schlanke Schlusszeile (BREAKING)

Die Footer-Komponente wurde von einem 3-Spalten-Sitemap-Raster auf eine
**schlanke einzeilige Schlusszeile** umgebaut. KT-1-Befund cld1-S21: das
Raster, in der Praxis mit nur einer Spalte befuellt, wirkte als abgebrochener
Stummel — nicht als Fusszeile.

Neue Form: links eine Identitaets-Zeile aus `|`-getrennten Segmenten (Marke,
Seiten-Kontext, optional ein Profil-Hydration-Slot), rechts die Rechtslinks
(`·`-getrennt) plus optionale Version, darueber ein feiner Hochstrich.

**Breaking — `FooterInput` umgestaltet:**

- `columns: list[FooterColumn]` → `segments: list[FooterSegment]` (linke Zeile)
- neu: `links: list[FooterLink]` — die Rechtslinks (vorher Teil der Spalten)
- entfernt: `note`, `user_info_id`, `user_info_label` — der Hydration-Slot
  wird jetzt ueber `FooterSegment.slot_id` ausgedrueckt
- `FooterColumn` entfaellt zugunsten von `FooterSegment` (`title`/`links` →
  `text`/`slot_id`)
- `version` unveraendert

Renderer-API (`render_footer_html` / `render_footer_css`) sowie die
`:focus-visible`-, XSS-Escape- und Token-Garantien bleiben. Konsumenten
(mkn-desk.com) ziehen mit v0.2.1 nach.

## [0.9.0] — 2026-05-20

### Hinzugefuegt — Hydration-Slots + Empty-State (UX-Welle B, Foundation)

Die Bausteine, die UX-Welle B fuer die Konsumenten-Migration und den
Platzhalter-Ausbau braucht. Additiv und **rueckwaertskompatibel zu v0.8.0**:
alle v0.8.0-Contracts und -Renderer bleiben unveraendert nutzbar, neue Felder
sind optional mit Default.

**Empty-State-Komponente** (`web/empty_state.py`): ruhiger Leer-Zustand —
gedaempfter Hinweistext statt Baustellen-Schild. Contract `EmptyStateInput`
(`message` Pflicht, `tier` optional fuer eine zarte farbliche Verankerung),
HTML- und CSS-Renderer, Pattern-Doku `_patterns/empty_state.md`. Keine neuen
Tokens — nutzt `--color-light-*` und die `--color-tier-*`-Familie aus v0.8.0.

**Brand-Bar Hydration-Slot** (`BrandBarInput.user_chip_id`): gesetzt rendert
die Brand-Bar nach den statischen Chips einen Lade-Chip mit dieser id, den
eine App client-seitig fuellt. `user_chip_label` traegt den
Server-gerenderten Pre-Hydration-Text.

**Footer Hydration-Slot** (`FooterInput.user_info_id`): optionaler
client-seitig gefuellter User-Info-Span in der Footer-Meta-Zeile.
`user_info_label` traegt den Pre-Hydration-Text.

**Tier-Chip Lade-Variante** (`.mn-tier-chip--loading`): neutraler,
gedaempft-kursiver Lade-Look fuer Hydration-Slots ohne bekannten Tier.

### Hintergrund

UX-Welle B Foundation. Spec: claudeAI
`docs/superpowers/specs/2026-05-20-ux-welle-b-design.md` Phase 1.

---

## [0.8.0] — 2026-05-20

### Hinzugefuegt — color.tier.* Token-Familie + 7 Web-Komponenten (UX-Welle v0.2)

Web-Tier-Farben fuer mkn-desk.com und die zugehoerige Komponenten-Schicht.

**Token-Familie `color.tier.*`** (16 Tokens): 4 Tier-Familien (bibliothek,
atelier, kabinett, start) x {bg, bg-soft, border, text}. `bg-soft` =
Sub-Nav-Hover, abgeleitet aus `bg` (55% ueber Weiss), vollwertiger Token
(cross-media-faehig). `start` referenziell auf `bibliothek` aliased.

**7 Web-Komponenten** (`web/`): Tier-Chip, Top-Nav (L1), Brand-Bar (L2),
Sub-Nav (L3), Page-Header, Footer, Content-Card + Card-Grid. Pattern-First
(Pydantic-Contract + Markdown-Spec + Renderer). PDF-Renderer folgen bei Bedarf.

### Hintergrund

UX-Aufwertung mkn-desk.com v0.2 — Foundation-Welle. Gemini-Gate-Review:
`bg-soft` als Token statt `color-mix` (Cross-Media-Faehigkeit), `start` als
Alias. Spec: claudeAI `docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md`.

---

## [0.7.0] — 2026-05-17

### Hinzugefuegt — Kachel-Token-Familie (KT-1 S256 TODO-1105)

Generische Token-Familie `kachel-*` fuer Sparkline-/KPI-Kacheln. Heute genutzt
von `system/lib/briefing/blocks/sparkline_kachel.py` (Finanz-Snapshot, 12
Symbole), spaeter wiederverwendbar fuer KPI-Tiles.

**Typography (size + leading):**
- `size.kachel-label` = 7pt (Symbol-Label oben links)
- `size.kachel-meta` = 6pt (Einheit, "vs MA50" oben rechts)
- `size.kachel-diff` = 9pt (Tages-Diff %-Wert mit Pfeil)
- `size.kachel-value` = 13pt (Hauptwert, wertgleich h3, eigene Semantik)
- `size.kachel-madiff` = 8pt (MA50-Diff %-Wert, wertgleich footer-page)
- + jeweilige leading-Tokens (1.21-1.31 Ratio)

**Spacing (`space.kachel.*`):**
- `inset` = 4pt (Text-Padding L/R)
- `radius` = 2pt (Eck-Rundung)
- `gap-col` / `gap-row` = 3mm (Grid-Abstaende)
- `width` = 38mm / `height` = 32mm (Komponenten-Dimensionen, 12 Kacheln auf A4)

**Strokes:**
- `stroke.kachel-marker` = 1.2pt (7T-Range-Marker-Linie)
- `stroke.kachel-trennlinie` = 0.3pt (zwischen Spark-/Text-Bereich)

### Hintergrund (KT-1 S256)

Die Sparkline-Kachel-Werte waren seit S241/S242 (Iter 15 final) als Modul-
Konstanten hardcoded — funktional korrekt, aber DS-Drift. KT-1's Direktive:
"DS bestimmt, nicht Renderer". Token-Familie statt Renderer-Konstanten,
generisches Naming (`kachel-*` statt `finanz-kachel-*`) fuer spaetere KPI-
Tile-Wiederverwendung.

**Heute nur helle Fassung**; Dark + Web-CSS-Pendant folgen.

### Konsumenten-Update

`claudeAI`: `system/lib/briefing/blocks/sparkline_kachel.py` wird auf
`size_token("kachel-label")` / `space_token("space.kachel.inset", unit="pt")`
etc. umgestellt (Folge-PR nach `pip install --upgrade mn-design-system`).

---

## [0.6.1] — 2026-05-16

### Geaendert
- `mn_design_system.__version__` wird jetzt zur Laufzeit via `importlib.metadata.version("mn-design-system")` aus dem installierten Wheel/Package-Metadata gelesen — **Single Source of Truth** ist die `pyproject.toml`-Version.
  - Vorher: hartkodierter String `"0.5.0"`, hing seit v0.5.0-Release fest. Drift gegen die installierte Wheel-Version (siehe `~/sync/channel-notes/2026-05-14-cld1-macb-design-system-drift-S12.md` von cld1-claude).
  - Fallback bei lokalem Source-Run ohne Install: `"0.0.0+local"`.

### Begründung

cld1-claude S12-Befund: drei inkonsistente Versionsindikatoren am Tag v0.5.4 — Wheel `0.5.4` / `__version__` `0.5.0` / `pyproject` `0.5.3`. Mit diesem Fix: alle drei Quellen sind nach Install konsistent.

---

## [0.6.0] — 2026-05-16

### Hinzugefuegt (vier neue typography-Tokens)
- `font.size.cover-hero` = **28pt** + `font.leading.cover-hero` = **34pt** — Cover-Hauptueberschrift fuer System-Doku-PDFs (war hardcoded `fontSize=28` in `system_doc_v2.py::cover_title`).
- `font.size.subsection` = **10.5pt** + `font.leading.subsection` = **14pt** — Subsection-Header. KT-1 S253: mehr Abstand zu body (9.5pt) als die alte hardcoded 10pt.
- `font.size.body-small` = **8.5pt** + `font.leading.body-small` = **11pt** — Body-Small fuer Annotationen, Fussnoten, sekundaeren Kontext. Eigener Name fuer Klarheit (gleiche Groesse wie caption, andere Semantik).
- `font.size.stat-display` = **20pt** + `font.leading.stat-display` = **24pt** — Statistik-Display fuer KPI-Tiles (war hardcoded `fontSize=20` in `system_doc_v2.py::stat_number`).

### Geaendert (KT-1 S253 — system-weite Typography-Skala)
- `font.size.title-section` — **18pt → 16pt** (+ leading 22pt → 20pt). KT-1: "18pt sind schon gross".
- `font.size.caption` — **9pt → 8.5pt** (+ leading 12pt → 11pt). System-weite Bildunterschrift-Skala.
- `font.size.code` — **9pt → 8.5pt** (+ leading 13pt → 11pt). System-weite Code-Snippet-Skala.

### Konsumenten-Auswirkung
Aenderungen an `caption`/`code`/`title-section` betreffen ALLE PDF-Renderer im PKA — bewusst gewollt fuer einheitliche Skala (KT-1: "dafuer ist design-system da"). Betroffen u.a.:
- `system/lib/briefing/modules/{header,bibel,tracker,aufgaben,projekte,...}_block.py` (caption-Token)
- `system/lib/briefing/renderers/_doc_helper.py` (caption)
- `system/lib/briefing/renderer_tech_ki.py`, `renderer_public.py` (disclaimer bleibt 8pt, caption wird kleiner)
- `.claude/skills/pdf-basis/scripts/pdf_utils.py` (zentrale Lib — bekommt parallelen Sweep, alle `# legacy:`-Hardcoded-Werte werden eliminiert)
- `.claude/skills/system-dokumentation/scripts/system_doc_v2.py` (Hauptanlass dieser Token-Welle)

### Konsum-Reihenfolge nach Release
1. `pip install --upgrade mn-design-system==0.6.0` in claudeAI-venv
2. Sweep aller 11 hardcoded-Files in claudeAI (separater PR)
3. PDFs regenerieren als Diff-Beweis

---

## [0.5.4] — 2026-05-13

### Geaendert
- `color.accent.warm.strong` — Amber-600 `#d97706` → **Copper-800 `#b45309`**.
  Warm-erdig statt orange; harmoniert besser mit der Indigo-Familie ohne den
  Sektions-Bruch-Charakter zu verlieren.
- `_meta`-Kommentar der `accent.warm`-Familie verlaengert um v0.5.4-Rationale.

### Hinzugefuegt
- `color.accent.warm.amber` — Legacy-Alias auf `#d97706` (war bis v0.5.3
  `color.accent.warm.strong`). Behalten fuer hochkontrastive Badge-Faelle,
  wo Copper-800 zu braun wirkt.

### Validierung
- WCAG-AA-Kontrast Copper-800 ↔ `accent.warm.soft`: **5.46:1** ✓
- WCAG-AA-Kontrast Copper-800 ↔ `light.bg`: 4.78:1 (Large only) — nur als
  Section-Header / Marker / Hairline einsetzen, nicht als Body.

### Status
Bug-Fix-Level nach SemVer-pre-1.0-Politik — kein Breaking-Change, der alte
Hex-Wert bleibt unter `color.accent.warm.amber` erreichbar. Diese Aenderung
wurde von KT-1 in S250 (Claude Web Design) ausgearbeitet; in S251 in das
upstream-Repo eingespielt. Versionsnummer urspruenglich als v0.3.1 geplant,
wegen Tag-Kollision (v0.3.1 = Welle E.0 Web-Renderer-Stubs) auf v0.5.4
korrigiert.

### Konsistenz-Korrektur (Generator-Drift)
- `tokens/spacing.json` — 8 Semantic-Spacing-Tokens (`tight-min`, `tight`,
  `default`, `wide`, `wide-max`, `section`, `divider`, `between-modules`)
  vom proprietaeren `ref`-Format auf Style-Dictionary-Alias-Syntax
  (`{space.N.value}`) umgestellt. Der Generator-Output enthaelt sie jetzt;
  vorher wurden sie still gedroppt und mussten manuell in `tokens.py`
  nachgepflegt werden.
- `tokens/typography.json` — 3 Font-Family-Tokens (`fallback-greek=STIXTwoMath`
  fuer Greek-Glyphen / Sigma-Rendering, `table-default=Geist`,
  `table-data=JetBrainsMono`) waren bisher nur in `mn_design_system/tokens.py`
  drift-manuell drin. Jetzt in JSON-SSoT gehoben → CI-Synced-Check gruen.

---

## [0.5.3] — 2026-05-10

### Fixed
- `fonts/__init__.py` — STIXTwoMath statt STIXTwoText-Greek fuer Greek-Glyphen
  (sigma/alpha/beta/...). v0.5.2 Greek-Variante hatte das Sigma-Render-Problem
  nicht geloest, weil STIXTwoText-Greek.ttf den PostScript-Namen
  `STIXTwoText-Regular` mit der Latin-TTF teilt (TTF-Asset-Bug von STIX). ReportLab
  cached intern per PS-Name → die zuerst registrierte Variante gewann → σ
  renderte als BOX-Glyph. Fix: STIXTwoMath als unabhaengige Font-Family registriert.

---

## [0.5.2] — 2026-05-10

### Fixed
- `helpers.font_with_fallback` nutzt jetzt `STIXTwoText-Greek` statt
  `STIXTwoText-Regular` fuer Greek-Letters. Vorher: σ wurde als
  BOX-Glyph (.notdef) gerendert, weil die Latin-TTF keine U+03C3-Glyphe
  enthielt (verifiziert via fontTools). (Anmerkung: v0.5.3 musste den
  PS-Namen-Konflikt nachfixen — siehe oben.)

---

## [0.5.1] — 2026-05-10

### Fixed
- `fonts/__init__.py` — STIXTwoText-Alias in `_FONT_MAP` ergaenzt.
  `helpers.font_with_fallback` wrappt Greek-Letters in `<font
  name="STIXTwoText">...</font>`-Tags; vorher war nur `STIXTwo` (kurz)
  registriert → ReportLab `ValueError` beim Rendern, claudeAI daily-engine
  Phase 4-render schlug fehl.

---

## [0.5.0] — 2026-05-09

### Added — fuer Welle 3 Briefing-Modul-Architektur (KT-1 S248)

- **Section-Title-Token** `font.size.title-section` = 18pt + leading 22pt
  (war hardcoded `fontSize=18` in pdf_utils title-Style)
- **News-Headline-Token** `font.size.news-headline` = 11pt + leading 14pt
  (News-Item-Headline, fett, ueber dem Body — Body bleibt 9.5pt einheitlich
  fuer alle News-Laengen, Length-Steuerung erfolgt im ETL-Layer ueber
  Wort-Limit, nicht ueber Schriftgroesse)
- **Semantische Spacing-Tokens** (waren hardcoded):
  - `space.semantic.sub-tight` = 0.5mm (Anriss-Bullet-spaceAfter)
  - `space.semantic.bibel-quelle` = 1.8mm (BibelQuelle-spaceBefore)
  - `space.semantic.tracker-item` = 1.5mm (Tracker-Item-spaceAfter)
  - `space.semantic.divider` = 4mm (section_divider() Spacing)
  - `space.semantic.between-modules` = 6mm (zwischen Modul-Bloecken)
- **Logo-Tokens** (waren hardcoded LOGO_SIZE/LOGO_GAP in pdf_utils):
  - `space.logo.size` = 18mm
  - `space.logo.gap` = 4mm
  - `space.logo.size-small` = 14mm

### Verworfen vs. v0.5.0-Plan

- News-Body-Length-spezifische Schrift-Tokens (`news-body-top/kurz/mittel/lang`):
  KT-1-Korrektur — Body bleibt **9.5pt einheitlich** fuer alle News-Laengen.
  Length-Differenzierung erfolgt im ETL-Layer ueber Wort-Limit (Vorschlag:
  top=20W, kurz=60W, mittel=100W, lang=200W — KT-1 prueft visuell).

---

## [0.4.4] — 2026-05-09

### Added
- **Token-Konsumtion-Helper-API** (KT-1 S248, Phase 0 der Welle Briefing-Drift-Beseitigung):
  - `space_token(key, unit="mm"|"pt"|"px"|"raw")` — Spacing-Token mit expliziter Einheit
  - `size_token(key, unit="pt"|"mm"|"px"|"raw")` — Schriftgroessen-Token
  - `leading_token(key, unit="pt"|"mm"|"px"|"raw")` — Leading-Token
  - `color_token(key)` — Farb-Token als Hex-String
  - `font_family(key)` — Font-Familien-Lookup
  - `font_with_fallback(text)` — wraped Greek/Math-Letters in
    `<font name="STIXTwoText">...</font>`-Tags fuer ReportLab (Sigma-Glyph-Bug-Fix)
  - Konvention: **1 unit = 1mm = 2.835pt = 4px** (mm-Basis, KT-1 misst auf A4
    nach Druck)
  - **Strict-Mode**: `KeyError` bei unbekanntem Token (Pattern 6, kein stilles Fallback)
- **Neue Use-Case-Tokens** (Footer-Familie KT-1 S248):
  - `font.size.title-page` = 22pt (war hardcoded fontSize=20 in renderer_v2.v2_title)
  - `font.size.footer-page` = 8pt (Page-Fusszeile am Seitenrand)
  - `font.size.disclaimer` = 8pt (End-of-Content "Generiert mit Claude...")
  - `font.size.source` = 8pt (Quellen-Verzeichnis direkt unter Hauptabsatz)
  - `font.size.icon-{large,medium,small}` = 22/14/11pt
- **Neue Severity-Tokens** (KT-1 S248 Variante F nach 6 PDF-Iterationen):
  - `color.severity.high` = `#dc2626` (red-600, leuchtender als status.error)
  - `color.severity.medium` = `#a16207` (amber-800, dunkel-warm Kupfer-Ton)
  - `color.severity.low` = `#6b7280` (alias auf color.text-muted)
  - Plus `*-bg`-Varianten fuer Severity-Badges
- **Neue Spacing-Klassen** (KT-1 S248 — kontextabhaengiges Spacing):
  - `space.semantic.tight-min` = 1mm (Mikro)
  - `space.semantic.tight` = 2mm (3-Spalten-Layout)
  - `space.semantic.default` = 3mm (Standard 1-spaltig)
  - `space.semantic.wide` = 5mm (Sektion-innerer Abstand)
  - `space.semantic.wide-max` = 8mm (vor Section-Header)
  - `space.semantic.section` = 12mm (zwischen Hauptsektionen)
  - `space.indent.{bullet,subitem,code}` = 3/6/4mm
- **Greek-Letter Fallback-Font-Token** `font.family.fallback-greek` = `STIXTwoText`
  (loest Sigma-Glyph-Bug aus Briefing-PDF "Vol-Spike +1,8 □")
- **Tabellen-Schrift-Tokens**:
  - `font.family.table-default` = `Geist` (Body-Konsistenz)
  - `font.family.table-data` = `JetBrainsMono` (Tabular Numerals fuer Zahlen)

### Changed
- **Repo-Hygiene**: BODY 10pt → 9.5pt und LEADING_BODY 15.5pt → 13.5pt
  (S242-Korrektur war im v0.4.3-Wheel, aber nicht in main committed) jetzt
  konsistent.

### Tests
- **38 neue Tests** in `tests/test_helpers.py` (alle gruen, total 133/133).

### Background
KT-1 S248-Tiefenanalyse heutiger Briefing-PDFs zeigte ~60 Drift-Stellen
(hardcoded `fontSize=N`, `leading=N`, `space*=N*mm`, Severity-Hex) in
`claudeAI`-Renderern. Wurzel: Token-Konsumtion-Infrastruktur fehlte. Diese
Release schliesst die Luecke. Phase 1-7 der Welle (Konsumenten-Migration in
claudeAI) folgen.

Plan: `claudeAI/.claude/plans/welle-briefing-design-drift-S248.md`.

---

## [0.4.3] — 2026-05-02

### Changed
- **KPI-Card Trend-Glyph konsistent in allen 3 Stufen** (KT-1 S241 B-7
  Briefing-Befund): Bullet "•" unter dem 0.5%-Schwellwert wirkte visuell
  deutlich kleiner als die ▲/▼-Triangle-Glyphen. Lesbarkeit bei
  Mikro-Bewegungen litt. **Neu:** alle drei Stufen tragen ▲ oder ▼ in
  derselben Groesse, nur die FARBE variiert (muted-grau bei <0.5%,
  success-gruen / error-rot ab 0.5%). Schwellwert-Logik (0.5%) bleibt
  unveraendert. Tests in `tests/components/pdf/test_kpi_card.py`
  entsprechend angepasst (4 Tests).

---

## [0.4.2] — 2026-04-30

### Added
- **Neue Token-Familie `color.accent.warm`** (Variante C', KT-1 S239
  nach Live-PDF-Vergleich):
  - `accent.warm-strong` = `#d97706` (Amber-600, kupferig-edel) — fuer
    Sektions-Header (Politik / Wirtschaft / Tech / ...).
  - `accent.warm-soft` = `#fef3c7` (Amber-100) — heller Tint-Hintergrund
    fuer Tagesfokus-Boxen u.ae.
  - `accent.warm-text` = `#78350f` (Amber-900) — kontrastsichere Schrift
    auf accent.warm-soft (>=4.5:1).
- Hierarchie-Logik: warmer Akzent als **Sektions-Bruch** (gliedert),
  kuehle Indigo-Familie als **Inhaltsanker** (Story-Titel in
  `color.h1` / Indigo-900). Hierarchie ueber Farbtemperatur, nicht
  ueber Helligkeit.

### Notes
- accent.warm ist **NICHT** als Status-Signal gedacht — semantische
  Trennung zu `status.warning` (Amber-500) und `status.urgent`
  (Orange-700). Kommentar in colors.json klargestellt.
- Konsumenten: Briefing-Renderer (`renderer_rich`, `renderer_public`)
  ziehen die Section-Header (`topnews_title` in
  `morgenbriefing_template.py`) auf das neue Token. Migration in
  claudeAI-Repo Schritt-fuer-Schritt nach Wheel-Release.

## [0.4.1] — 2026-04-30

### Changed
- **`KpiCardInput.trend_direction()` Schwellwert 0.01 → 0.5.** KT-1
  Briefing-Befund 30.04.2026 (S239 B5): Mikro-Bewegungen <0.5% sollen
  visuell zurueckgenommen werden statt rot/gruen einzufaerben.
- **`components/pdf/kpi_card._format_change`** zeigt fuer `|Δ|<0.5%`
  jetzt einen Bullet-Punkt `•` in `color.viz.muted` (#b0bec5) statt
  Pfeil + Status-Farbe. Vorzeichen wird manuell gerendert
  (`+0,30%` / `-0,20%`). Aufruf ohne Bullet/Pfeil bei `|Δ|>=0.5%`
  bleibt unveraendert.

### Updated
- Pattern-Spec `components/_patterns/kpi_card.md` § "Verhalten" und
  Token-Liste auf neuen Schwellwert + `color.viz.muted` aktualisiert.

### Tests
- 6 neue Tests in `tests/components/pdf/test_kpi_card.py` decken die
  Schwellwert-Stufen ab (knapp unter 0.5%, an der Schwelle, deutlich
  ueber, exakte Null, negative Mikro-Bewegung).

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
