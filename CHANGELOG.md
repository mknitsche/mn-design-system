# Changelog

Alle nennenswerten Aenderungen am MN PKA Design-System.

Format: [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) · SemVer pre-1.0
(Solo-Maintainer-Modus): `0.x.0` = neue Komponente/Token-Familie, `0.x.y` = Bugfix
oder Doku.

---

## [0.18.2] — 2026-10-17

### Behoben
- **KpiCard:** das Label trennt deutsche Komposita nach Silben (`hyphens: auto`, Seite `lang="de"`) und
  bricht als letzte Stufe um, statt aus der Karte zu laufen — „TRAININGSBELASTUN / G“ auf 390 px (mkn-desk,
  Observatorium Sport). Browser-Test `TestKpiLabelSchmal`.
- **TierChip:** der Fallback hinter `var(--color-tier-<tier>-*)` war fuer jeden Tier das Gruen der Bibliothek;
  er ist jetzt der Token-Wert des eigenen Tiers (`tokens.get`). Browser-Test `TestTierChipFallback`.

## [0.18.1] — 2026-10-17

### Behoben

- **verlauf_chart:** die rechte Werteachse traegt keinen Namen mehr. Er stand oben rechts genau auf der Legende („7-Tage-Summe“), sichtbar bei 390 und 1440 px im Konsumenten (mkn-desk Observatorium). Die Einheit steht an der linken Achse; welche Reihe rechts liegt, sagen Legende und Bildunterschrift.

## [0.18.0] — 2026-10-17

> Versionsnummer nach der Regel in `README.md` (neue Komponente und neue Token-Familie = Minor-Sprung): bis zum Review als 0.17.1 gebaut, vor dem ersten Tag auf 0.18.0 gehoben (Critic-Befund MITTEL).

### Neu — Tier magazin, KPI-Polaritaet, Zeitraum-Leiste, zweite Werteachse (claudeAI TODO-885 Welle C)

Alles additiv: ein Aufruf aus 0.17.0 liefert dieselbe Ausgabe — mit EINER gewollten
Ausnahme, der Zielband-Bildunterschrift des Verlauf-Charts (siehe unten).

- **Tier `magazin`** (gedaempfte Grau-Nuance): `WebTier.MAGAZIN`, Tokens
  `color.tier.magazin.{bg,bg-soft,border,text,hover-on-dark}`. `bg`, `border` und `text`
  referenzieren die Grau-Skala (`grey.50` = `#f5f5f5`, `grey.200` = `#e5e7eb`,
  `grey.700` = `#374151`), `bg-soft` ist `bg` zu 55 % ueber Weiss (`#fafafa`, wie bei den
  anderen Tiers gebildet), `hover-on-dark` der halbtransparente Rand
  (`rgba(229,231,235,0.5)`). Text-Kontrast 9,45:1 auf `bg`, 9,88:1 auf `bg-soft`, 10,31:1 auf
  Weiss (Test: >= 4,5:1). Eingetragen in Masthead, Tier-Chip, Sub-Nav, Content-Card und
  Empty-State; ein aus dem Enum abgeleiteter Test prueft die Wirkung je Komponente, damit
  ein kuenftiger Tier nicht wieder in einer der fuenf Listen fehlt.
- **KpiCard: Polaritaet und deutsches absolutes Delta.** `KpiCardInput` bekommt
  `richtung: "hoeher" | "niedriger" | "neutral" = "hoeher"`, `delta_wert: float | None`,
  `delta_einheit: str = ""`, `dezimalstellen: int = 1` (0..6). Neu am Vertrag:
  `KpiWertung` (`GUT`/`SCHLECHT`/`NEUTRAL`), `wertung()` und `delta_text()`;
  `trend_direction()` liest bei gesetztem `delta_wert` das Delta. Die Farbe folgt der
  Wertung (Bewegung x Polaritaet): bei `"niedriger"` ist ein Rueckgang gruen, bei
  `"neutral"` bleibt alles gedaempft; der Pfeil zeigt immer die Bewegung. Web: neben
  `is-up`/`is-down`/`is-neutral` traegt das Delta bei `richtung != "hoeher"` eine
  Wertungsklasse `is-gut`/`is-schlecht`/`is-ungewertet`, die im CSS danach steht. Das
  absolute Delta steht deutsch: „+1,2 kg" / „−1,2 kg" (Dezimalkomma, Tausenderpunkt ab
  1.000, Minuszeichen U+2212, geschuetztes Leerzeichen U+00A0 vor der Einheit); rundet es
  auf null, steht „unverändert" (Bewegung neutral). Web und PDF teilen den Vertrag, der
  PDF-Renderer ist nachgezogen.
- **Komponente `zeitraum_leiste`** (Web): Segment-Leiste aus Links fuer `?tage=30|90|365`.
  `ZeitraumLeisteInput` (`optionen` 2..6, `aria_label` = „Zeitraum"), `ZeitraumOption`
  (`label`, `href`, `active`); `render_zeitraum_leiste_html()` / `render_zeitraum_leiste_css()`.
  Die gewaehlte Option traegt `aria-current="page"` — der aktive Zustand haengt allein an
  diesem Attribut. Jede Option ist mindestens 44 x 44 px, der Fokusring liegt innen. Kein
  Skript, nichts inline. Vorbild war die Repo-CSS `.verlauf-fenster` des Konsumenten, die
  damit entfallen kann.
- **Tokens `web.touch-target` (`44px`) und `web.scroll-max-h` (`22rem`)** fuer das
  Touch-Ziel und die Hoehe eines scrollenden Tabellen-Bereichs.
- **Verlauf-Chart: zweite Werteachse.** `VerlaufReihe.achse: "links" | "rechts" = "links"`:
  liegt eine Reihe rechts, ist `yAxis` der Option eine Liste aus linker und rechter Achse und
  jene Reihe zeigt mit `yAxisIndex: 1` auf die rechte (z. B. 7-Tage-Summen neben
  Tageswerten). Ohne rechte Reihe bleibt `yAxis` EIN Objekt — die Option ist bytegleich zu
  0.17.0 (8 Faelle gegen `git archive` von 0.17.0 verglichen).
- **Verlauf-Chart: Zielband-Bildunterschrift ohne ueberfluessige Nullen:** „Zielband 70–74 kg"
  statt „70,0–74,0 kg", „72,5–74", „1.000–1.500 kcal"; ein negativer Wert traegt das
  Minuszeichen U+2212. **Das ist die einzige sichtbare Aenderung fuer bestehende Aufrufer.**
- **Verlauf-Chart: Browser-Test** fuer den Fall, dass die erste Reihe im Fenster keinen Punkt
  hat, das Zielband aber an ihr haengt (Critic-Hinweis 0.17.0, bis jetzt ungeprueft):
  ECharts zeichnet das Band trotzdem; kein Code geaendert.

### Entscheidungen im Bau (Abweichungen vom Auftrag, begruendet)

- **`change_pct` und `delta_wert` zugleich sind ein `ValidationError`.** Der Auftrag nennt
  beide als optional, regelt den gemeinsamen Fall aber nicht; die Karte zeigt genau EIN Delta,
  und eine still verworfene Zahl ist der schlechtere Ausgang. Ebenso `delta_einheit` ohne
  `delta_wert`. `delta_wert` lehnt NaN/Infinity ab.
- **Rundung des Deltas kaufmaennisch** (halb aufwaerts, aus der kuerzesten Dezimaldarstellung):
  0,25 -> „0,3", 0,35 -> „0,4" (als Gleitkommazahl 0,3499…). Der Rundungsmodus von `format`
  wuerde 2,5 zu „2" machen. Die bestehende Zahl-Schreibweise des Verlauf-Charts (`zahl_de`)
  bleibt unveraendert (Aufrufer duerfen sich nicht aendern) — im Delta rundet also etwas
  anders als in der Beschreibung des Charts, nur auf exakten Halbwerten.
- **Prozentwert bleibt im bisherigen Format** (Web „+1.25%" mit Punkt, PDF „+1,25%"): „exakt
  gleich" fuer alte Aufrufer. Nur das neue absolute Delta ist durchgehend deutsch gesetzt.
- **„unverändert"** zeigt der Web-Renderer mit ■ (wie jede neutrale Bewegung), der PDF-Renderer
  ohne Pfeil: die PDF-Schrift (Geist) hat kein ■.
- **Zeitraum-Leiste: kein Aussenabstand** (die Repo-CSS hatte `margin: 0 0 var(--space-4)`); den
  setzt der Konsument. Hover-Grund `color.light.surface-subtle` statt `grey.100`, Rahmen
  `web.color.separator` — DS-Tokens statt der Konsumenten-Aliase. Zusaetzlich `min-width`
  (ein kurzes Label wie „7" waere sonst schmaler als ein Finger). Hoechstens eine Option aktiv;
  keine aktive ist erlaubt (`?tage=7` steht in keiner Option). Kontraste: ruhend 4,83:1,
  Hover 14,79:1, aktiv 5,62:1 (Test: >= 4,5:1).
- **Verlauf-Chart, zweite Achse:** beide Achsen tragen dieselbe Einheit (`einheit`) — fuer
  7-Tage-Summen neben Tageswerten reicht das; eine eigene Einheit der rechten Achse waere ein
  weiteres Feld und bleibt aus, bis ein Verwender sie braucht. Die **erste Reihe muss links
  liegen** (`ValidationError` sonst): an ihr haengen Zielband, Marken und die Beschreibung, und
  das Band stuende bei einer rechten ersten Reihe auf der falschen Skala. Die linke Achse und
  ihre festen Grenzen richten sich nur nach den linken Reihen; der rechte Rand wird 48 px breit
  (sonst wuerde die Beschriftung abgeschnitten); die Textlegende nennt „(rechte Achse)".
- **Loader:** setzt das deutsche Zahlenformat auf jede Werteachse (`yAxis` kann eine Liste
  sein); fuer eine einzelne Achse ist das Verhalten unveraendert.
- **Intern:** die deutsche Zahlenschreibweise zog aus `_patterns/_verlauf.py` nach
  `_patterns/_zahl.py` (unveraendert), dort kommen `zahl_de_kurz`, `rundet_auf_null` und
  `delta_de` dazu.

### Tests

`tests/test_zahl.py` (Format), `tests/test_kpi_card_vertrag.py` (Vertrag), `tests/components/web/test_kpi_card.py`
und `tests/components/pdf/test_kpi_card.py` (alte Aufrufe bytegleich, Wertung), `tests/components/web/test_zeitraum_leiste.py`,
`tests/components/web/test_tier_vollstaendigkeit.py`, `tests/components/web/test_kpi_zeitraum_browser.py`
(Farbe des Deltas, Touch-Ziel, Zustaende, Fokus, Navigation ohne JavaScript — im Browser) sowie
Ergaenzungen in `test_verlauf_chart*.py`, `test_tokens_tier.py`, `test_contracts_web.py`,
`test_web_foundation_tokens.py`. Waechter-Tests sind per Mutation geprueft.

## [0.17.0] — 2026-10-17

### Neu — Tier observatorium, Komponente verlauf_chart (claudeAI TODO-885 § 4.10a)

Der neue Bereich Observatorium (Gesundheits- und Sportwerte, AMBER, nur der Eigentuemer) braucht
einen eigenen Tier und ein Zeitreihen-Diagramm. Beides kommt additiv in EINEM Release: kein
bestehender Verwender bricht.

- **Tier `observatorium`** (Alias auf `atelier`, wie `start` auf `bibliothek` verweist):
  `WebTier.OBSERVATORIUM`, Tokens `color.tier.observatorium.{bg,bg-soft,border,text,hover-on-dark}`
  als Referenzen auf `color.tier.atelier.*` — AMBER-Werte unter eigenem Namen, eine eigene Nuance
  spaeter ohne Konsumenten-Aenderung. Eingetragen in Masthead, Tier-Chip, Sub-Nav, Content-Card
  und Empty-State (jede dieser Komponenten fuehrt eine eigene Tier-Liste; ohne Eintrag bekaeme die
  Sub-Nav des neuen Bereichs keine Hover- und Aktiv-Farbe).
- **Komponente `verlauf_chart`** auf Apache ECharts 6.1.0, selbst gehostet. Vertrag
  `VerlaufChartInput` (+ `VerlaufReihe`, `VerlaufPunkt`, `VerlaufMarkierung`): 1..4 Reihen, Zeitfenster
  `von`/`bis`, optionales Zielband, bis zu 12 Ereignis-Marken, feste Hoehenstufen (CSS-Klasse, nie
  `style=`), `datetime` ohne Zeitzone gilt als Europe/Berlin, NaN/Infinity abgelehnt.
  `verlauf_chart_option()` ist reines JSON ohne Farbe und ohne Funktion;
  `render_verlauf_chart_html()` legt es als `<script type="application/json">`-Datenblock ab
  (`<` als `\u003c`) und liefert Flaeche, Textlegende und `aria-label`;
  `echarts_theme("hell"|"dunkel")` baut das Theme aus den Tokens; `render_verlauf_chart_js()` ist
  der Loader (deutsches Zahlen- und Datumsformat per `Intl`, `ResizeObserver`, Theme-Wahl,
  `prefers-reduced-motion`); `render_verlauf_chart_css()` liefert Layout und sechs Hoehenklassen.
  Alles laeuft unter `script-src 'self'` / `style-src 'self'` — kein Inline-Skript, kein Inline-Stil,
  kein CDN. Spec: `components/_patterns/verlauf_chart.md`.
- **Vendoring Apache ECharts 6.1.0** unter `mn_design_system/vendor/echarts/` (Apache-2.0, LICENSE,
  NOTICE und `licenses/LICENSE-d3` byte-gleich aus dem npm-Tarball — der Build enthaelt d3.js-Code
  (BSD-3, Mike Bostock), auf dessen Lizenztext die ECharts-LICENSE verweist und der bei der
  Weitergabe mitgehen muss; `VENDOR.json` mit Pin, SHA-256 und Tarball-Integrity;
  `vendor_js_dir()`, `ECHARTS_DATEI`, `ECHARTS_VERSION` in `components.web`). **Datei: der
  `common`-Build `echarts.common.min.js`** (715 KB, 240 KB gzip), SHA-256 `61f13280…b013d5`. Die
  volle `echarts.min.js` (1,1 MB, SHA-256 `b66b25ae…0fd0`) ist bewusst NICHT vendort: der Plan
  nannte irrtuemlich deren Hash fuer die common-Datei; massgeblich ist die Tarball-Integrity
  (`sha512-q0yaFPgg…`), die mit der Registry uebereinstimmt. Dass der common-Build alles enthaelt,
  was die Option benutzt (Linie, Zeitachse, Tooltip, Legende, dataZoom inside + slider, markArea,
  markLine, graphic, aria), beweist `tests/components/web/test_verlauf_chart_browser.py` per
  Ausfuehrung in Chromium unter strenger CSP — jeder Baustein mit sichtbarer Wirkung (Pixel,
  Zoom-Zustand, Attribut), nicht per Textsuche: ECharts meldet einen fehlenden Baustein im
  Minify-Build nicht. `package-data` liefert `vendor/**` mit aus.

### Entscheidungen im Bau (Abweichungen vom Plan-Wortlaut, begruendet)

- **Theme-Text:** gedaempfter Text (`color.{light,dark}.text-muted`) statt `color.grey.600` — das
  Token ist `#999999` (2,8:1 auf Weiss), Achsenbeschriftung braucht 4,5:1; ein Test prueft den
  Kontrast.
- **Zeitfenster:** `bis` gilt einschliesslich (`xAxis.max` = Ende des Tages): ein Blutdruck um 07:30
  am letzten Tag verschwaende sonst.
- **Zahlenformat im Loader:** Komma, Tausenderpunkt und `dezimalstellen` kann reines JSON nicht
  ausdruecken; der Loader setzt Achsen- und Tooltip-Formatierer aus `data-dezimalstellen`.
- **Zielband:** feste, runde Achsengrenzen, weil `markArea` die Achse nicht erweitert. Im
  dunklen Theme ist das Band `color.status.success` mit Deckkraft 0,2 (das helle `success-bg`
  wuerde auf dunklem Grund blenden).
- **Raender:** `grid` 48/12/32/56 statt 48/12/16/40 (links/rechts/oben/unten): oben ist Platz
  fuer Einheit und Legende, unten fuer Achsentext und die Zoom-Leiste (18 px hoch, 6 px Rand).
- **Gitter dunkel:** `color.dark.border` (nicht `grey.600`, wie der Plan fuer Hell/Dunkel
  gemeinsam nennt) — dieselbe Kontrast-Begruendung wie beim Text.
- **Mausrad zoomt nur mit Strg** (`touch-action: pan-y` am Diagramm): sonst liesse sich die Seite
  unter dem Zeiger nicht mehr scrollen.
- **Hoehe** als `height` (nicht `min-height`): feste Hoehe vermeidet eine Rueckkopplung zwischen
  Canvas und `ResizeObserver`.
- **Leeres Fenster:** Achse und Hinweis „keine Werte im Fenster", ohne Zoom-Leiste.

### Tests

`tests/test_vendor_echarts.py` (Hash, Lizenz, jeder `/licenses/`-Verweis der LICENSE hat seine
Datei, package-data), `tests/test_contracts_web.py`
(Vertrag), `tests/components/web/test_verlauf_chart.py` (Option, HTML, Theme, Loader, CSS),
`tests/components/web/test_verlauf_chart_browser.py` (Wirkung im Browser, nur mit Playwright +
Chromium, sonst sichtbar uebersprungen). Waechter-Tests sind per Mutation geprueft.

## [0.16.1] — 2026-10-13

### Geaendert — STIX Two Math 2.13 unter der OFL (KT-1-Entscheid 2026-10-13)

- **STIX Two Math auf Version 2.13** (`v2.13b171`, stipub/stixfonts): bis 0.16.0 lag Version
  2.02 bei, deren Metadaten auf die STIX Fonts User License verweisen (Bedingungen fuer
  jeden, der die Schrift bezieht) — README und CITATIONS behaupteten bis 0.16.0 OFL. 2.13
  steht unter der SIL OFL 1.1, bringt 4.605 statt 4.138 Glyphen, und der Rueckfall fuer
  Griechisch/Mathe (`font_with_fallback`, Token `font.family.math`/`fallback-greek`) setzt
  σ, α, β, ≤, ∑ korrekt (PDF-Probe; nicht pixelgleich — die Laufweiten weichen um
  Subpixel ab). Der PostScript-Name aendert sich von `STIXTwoMath` zu
  `STIXTwoMath-Regular` und ist weiter eindeutig, die S249-Kollision mit STIX Two Text
  kehrt nicht zurueck.
- **Datei:** `STIXTwoMath-Regular.ttf` (gleicher Name, neue Fassung); die OpenType-Fassung
  heisst jetzt wie upstream `STIXTwoMath-Regular.otf` statt `STIX2Math.otf` (kein Code
  und kein Verwender nennt den alten Namen).
- **Lizenzrumpf wortgleich mit der SIL-Vorlage:** „PERMISSION & CONDITIONS“ statt „AND“ in
  allen `OFL.txt` (die Kopfzeilen tragen bewusst die Copyright-Zeilen der Schriftdateien) (0.16.0 hatte die Abweichung von der Geist-Vorlage uebernommen, ein Test
  schrieb sie fest); `stix-two/OFL.txt` ist der Text des Upstream-Projekts; `geist/OFL.txt`
  traegt die Zeile der Schriftdateien („Copyright 2024 The Geist Project Authors“) statt der
  veralteten Upstream-Zeile („2023 Vercel“) — der Copyright-Test schliesst Geist nicht mehr aus.
- **Waechter:** jede Schriftdatei einer OFL-Familie muss laut IHRER Lizenz-URL (name-ID 14)
  auf die OFL verweisen — der Test faellt mit der alten STIX-Math-Datei, auch wenn deren
  Beschreibungstext „based on the SIL Open Font License“ sagt.

## [0.16.0] — 2026-10-13

### Neu — Schnitt-Tokens, Web-Schriftketten, Stufe display (claudeAI TODO-887)

Die Verwender trugen Schnittnamen und Rueckfallketten als Literale in eigenen Tabellen;
ein Schriftwechsel im Design-System zog dort nicht nach. Jetzt kommen sie als Tokens.

- **Schnitt-Tokens (PDF):** `font.family.sans-bold` (Geist-Bold), `sans-medium`
  (Geist-Medium), `sans-light` (Geist-Light), `mono-bold` (JetBrainsMono-Bold),
  `italic-editorial-bold` (SourceSerif4-BoldItalic). Alle sind bei ReportLab angemeldet.
- **Web-Tokens:** `web.font.mono` („JetBrains Mono“) und die Rueckfallketten
  `web.font.stack.sans`, `web.font.stack.serif-editorial`, `web.font.stack.mono`. Es wird
  KEINE Web-Datei fuer die Mono mitgeliefert: sie muss lokal installiert sein, sonst
  greift die Kette.
- **Stufe display:** `web.text.display` = 40px, `web.leading.display` = 1.1 (Hero-Titel).
  `render_foundation_css()` setzt sie mobil eine Stufe zurueck, auf den Desktop-Wert von
  `web.text.h1` (33px; aus dem Token, kein Literal).
- **`css_font_stack(art)`** (`components.web`, auch exportiert): liefert den vollstaendigen
  `font-family`-Wert — die Familie in Anfuehrungszeichen plus Rueckfallkette aus den
  Tokens. `art` ist `"sans"`, `"serif-editorial"` oder `"mono"`; alles andere ist ein
  `KeyError`. Die Anfuehrungszeichen sind noetig, weil „Source Serif 4“ ungequotet kein
  gueltiger CSS-Familienname ist.
- **Lizenztexte je Schriftfamilie:** `OFL.txt` fuer Source Serif 4, Source Sans 3,
  JetBrains Mono, Inter, Noto Sans, STIX Two und die Web-Schriften (`fonts/web/`),
  `LICENSE` (MIT) fuer Phosphor. Die Copyright-Zeilen stammen aus den Metadaten der
  Schriftdateien (name ID 0), nicht aus dem Gedaechtnis. Die SIL OFL 1.1 verlangt, dass
  jede weitergegebene Kopie den Vermerk und den Text enthaelt; bis 0.15.0 lag nur bei
  Geist einer bei. Ein Test prueft, dass jede Familie im Paket ihren Text hat und dass
  die Copyright-Zeile darin steht.

### Behoben

- **Fett in der Zitat-Kursive:** `font_family("italic-editorial")` als GRUNDSCHRIFT eines
  Paragraphs ergab bei `<b>` still den Grundschnitt (alle Fragmente „SourceSerif4-Italic“;
  Probe 2026-10-13). „SourceSerif4-Italic“ ist jetzt eine Familie: `<b>` und `<b><i>`
  ergeben `SourceSerif4-BoldItalic`. Belegt am `Paragraph.frags`, nicht an einer Tabelle.
- **KPI-Karte (PDF):** die Caption-Schrift war das Literal „SourceSerif-Italic“, jetzt
  `font_family("italic-editorial")` — und damit gilt dort dieselbe Familie (`<b>` wirkt).
- **`dist/css/tokens.css` quotet die Web-Schriftnamen:** `--web-font-serif-editorial`
  stand dort als `Source Serif 4` ohne Anfuehrungszeichen. Wer `tokens.css` laedt, bekam
  damit fuer Wortmarke und Initiale (`var(--web-font-serif-editorial, …)`) eine zur
  Berechnungszeit ungueltige Deklaration — die Schrift fiel still auf die geerbte zurueck.
  Ein Build-Transform quotet jetzt `web.font.*` (nicht die Rueckfallketten). Die
  Python-Tokens bleiben ungequotet; claudeAI setzt die Variablen selbst gequotet und war
  nicht betroffen.
- **Geist-Light als Grundschrift:** jetzt eine Familie — `<b>`/`<i>` nehmen die
  Geist-Standardschnitte statt still im Light-Schnitt zu bleiben.
- **Chat-Baustein (Web):** Code und Werkzeug-Abzeichen nahmen `var(--font-family-mono, …)`
  — das ist der PDF-Name „JetBrainsMono“, kein Web-Familienname; wer `tokens.css` laedt,
  bekam damit keine Monospace-Schrift. Jetzt `var(--web-font-mono, …)`.
- **Schnittnamen im Design-System selbst:** KPI-Karte und Wetter-Streifen setzen
  `font_family("sans"|"sans-bold")` statt der Literale „Geist“/„Geist-Bold“.
- **Lizenzangaben:** JetBrains Mono steht unter der SIL OFL (laut Schriftdatei), nicht
  unter Apache 2.0 wie in README/CITATIONS behauptet. STIX Two Math (Version 2.02)
  verweist auf die STIX Fonts User License (auf OFL-Basis), nicht auf OFL 1.1; NOTICE
  nennt die Ausnahmen jetzt (STIX Math, Phosphor MIT). CITATIONS ergaenzt Inter und Noto;
  der Satz „TTF nicht eingecheckt“ war falsch. Die README-Statustabelle (stand bei
  v0.3.0) verweist jetzt auf diesen CHANGELOG.
- **Schriften werden nicht mehr still verschluckt:** ein Schnitt, den ReportLab nicht
  laden kann, steht jetzt als Warnung im Log (`mn_design_system.fonts`), statt per
  `except: pass` spurlos zu fehlen.

### Intern

- Alle `ruff check`-Funde behoben (I001, RUF022, RUF100, PYI041, FLY002, S110), sauber
  unter ruff 0.16 und dem in pre-commit gepinnten 0.15.8 (E402 durch Importe am Dateianfang);
  `ruff format` inklusive der README-Codebloecke.
- `tokens.py` und `dist/css|json|latex/tokens.*` sind per `npm run build` erzeugt.
  Ein Test prueft, dass `dist/json/tokens.json` und `tokens.py` uebereinstimmen.

**Fuer Konsumenten:** Token-Namen und Funktionen sind unveraendert und nur ergaenzt;
geaendert hat sich der WERT von `--web-font-*` in `tokens.css` (jetzt mit
Anfuehrungszeichen).
Sichtbare Unterschiede: `<b>` in der Zitat-Kursive und in Geist-Light wirkt jetzt; die
KPI-Karte nennt ihre Caption-Schrift „SourceSerif4-Italic“ (dieselbe Datei);
`render_foundation_css()` hat eine Zeile mehr (`--web-text-display` mobil); `tokens.css`
quotet `--web-font-*`; eine nicht ladbare Schrift steht als Warnung im Log. Neu zu verwenden: `css_font_stack("sans" | "serif-editorial" | "mono")`
statt eigener `font-family`-Literale; die Schnitt-Tokens statt eigener Namenstabellen.

## [0.15.0] — 2026-10-13

### Behoben — Fett und Kursiv sind in ReportLab-PDFs wieder sichtbar

`register_all_fonts()` meldete jeden Schnitt einzeln an, aber keine **Familie**.
ReportLab loest `<b>`/`<i>` in einem Paragraph ueber die Familien-Zuordnung auf und
setzte ohne sie still den Grundschnitt: Hervorhebungen waren in allen ReportLab-PDFs
der Konsumenten unsichtbar (Deep-Research-Berichte, Dossiers, Briefing). Jetzt werden
die Familien Geist, Geist Medium, Source Serif, Source Sans, Inter, Noto Sans, STIX Two
(auch unter STIXTwoText), JetBrains Mono sowie die Ersatznamen Helvetica und Arial
angemeldet. Wo ein Schnitt fehlt, steht der naechstliegende vorhandene da (STIX Two:
Fett fuer Fett-Kursiv; JetBrains Mono: Code bleibt aufrecht).

- **Zitat-Token:** `font.family.italic-editorial` lieferte seit v0.5.0
  „SourceSerif4-Italic“, angemeldet war die Schrift nur als „SourceSerif-Italic“ —
  wer den Token nahm, bekam einen `ValueError`. Der Token-Name ist jetzt zusaetzlich
  angemeldet (der Token selbst bleibt: LaTeX braucht den Dateinamen).
- **Toter Eintrag:** `STIXTwo(Text)-BoldItalic` zeigte auf eine nicht vorhandene
  Datei und wurde still uebersprungen; entfernt.

### Neu — Geist kursiv, Web-Schriften aus dem Design-System

- **Geist Italic, Medium Italic, Bold Italic** (Geist 1.800, SIL OFL 1.1, Lizenztext
  `fonts/geist/OFL.txt`). Geist hatte bei der Stack-Wahl (S238) keinen Kursiv-Schnitt;
  daher die beiden Ersatzloesungen, die jetzt entfallen:
  - `font.family.italic-ui`: **Geist-Medium → Geist-MediumItalic** (Status-Markierung
    ist jetzt wirklich kursiv, weiterhin ohne Bruch zwischen Grotesk und Serife).
  - Die Helvetica-/Arial-Ersatznamen fuer Kursiv zeigen auf **Geist Italic** statt auf
    Source Serif Italic.
  - `font.family.italic-editorial` (Source Serif 4 Italic fuer Zitate, Captions,
    Initialen) bleibt unveraendert — das ist ein bewusster Kontrast, keine Ersatzloesung.
- **Web-Schriften im Paket** (Geist 300/400/500/700 aufrecht, 400/500/700 kursiv, Source Serif 4 kursiv): `fonts/web/*.woff2` plus `components.web.WEB_SCHRIFTEN`,
  `render_font_face(url_prefix)` und `web_font_dir()`. Bis 0.14.2 lagen die woff2-Dateien
  und die Schnitt-Liste beim Konsumenten; ein Schriftwechsel im Design-System zog im
  Web nicht nach, und der Browser schraegte Geist kuenstlich an.

**Fuer Konsumenten:** `register_all_fonts()` genuegt — die Familien kommen mit. Es muss
vor der ersten ReportLab-Nutzung laufen: ReportLab ueberschreibt einen schon geladenen
Namen nicht, sonst bleibt fuer „Helvetica" die eingebaute Type-1-Schrift.
Web: `render_font_face("/assets/fonts/")` einbinden und die Dateien aus
`web_font_dir()` ausliefern.

## [0.14.2] — 2026-10-04

### Behoben — Sub-Nav auf dem Handy: weitere Reiter sichtbar, aktiver Reiter im Bild; Masthead bei 320 px

Zwei Befunde aus dem Durchklick von mkn-desk.com auf dem Handy. Alles nur im
Bereich unter `web.layout.bp-tablet` (Desktop pixelgleich), Werte aus den Tokens.

- **Sub-Nav, Rand-Hinweis (reines CSS):** die scrollbare Leiste zeigt an ihren
  Raendern, dass es weitergeht — ein Schatten (`web.color.separator`, `space.4`)
  genau dort, wo dahinter noch Reiter liegen. Links erscheint er erst nach dem
  Scrollen, rechts verschwindet er am Ende; passen alle Reiter, gibt es keinen
  Hinweis. Technik: zwei mitscrollende Deckflaechen in `color.light.surface`
  (`background-attachment: local`) verdecken zwei am Rand stehende Schatten.
  Funktioniert **ohne Skript**; keine Animation.
- **Sub-Nav, aktiver Reiter im Ausschnitt:** `scroll-initial-target: nearest` mit
  `scroll-snap-align: center` am aktiven Tab rollt die Leiste beim Laden mittig
  auf ihn (beide Nachbarn bleiben sichtbar). Es scrollt nur die Leiste, nie die
  Seite. Diese Property kennt nur **Chromium (ab 133)**; Safari und Firefox
  brauchen den Rueckfall unten.
- **Masthead:** die Tier-Pillen (`.mn-masthead__pills`) duerfen umbrechen
  (`flex-wrap: wrap`). Auf 320 px war die Pillen-Zeile 9 px zu breit und
  verbreiterte die Seite. Gemessen (Chromium, Geist): die Zeile ist 313 px breit
  und bleibt eine Zeile ab 345 px (alle gaengigen Handys); von 320 bis 344 px sind es
  zwei Zeilen. Das Umbrechen gilt bei jeder Breite (nicht nur unter bp-tablet), wirkt
  aber erst unter 345 px. Das Masthead bleibt breakpoint-frei.

### Hinzugefuegt — `render_sub_nav_js()` (optionales Skript fuer Safari und Firefox)

`mn_design_system.components.web.render_sub_nav_js()` liefert ein kleines Skript,
das den aktiven Tab der scrollbaren Sub-Nav mittig ins Bild rollt — dieselbe
Position, die Chromium per CSS erreicht. **Optional:** wer es weglaesst, verliert
nur das Zentrieren in Safari und Firefox; der Rand-Hinweis bleibt.

**Einbindung durch den Konsumenten:**

1. Beim Seitenbau den Text als **eigene Datei** ablegen, empfohlener Name
   `mn-sub-nav.js` (neben dem CSS aus `render_sub_nav_css()`):
   `Path("static/mn-sub-nav.js").write_text(render_sub_nav_js())`.
2. Auf jeder Seite mit Sub-Nav im `<head>` einbinden:
   `<script src="/static/mn-sub-nav.js" defer></script>`. `defer` wird empfohlen,
   ist aber keine Pflicht — das Skript wartet im `<head>` selbst auf das fertige
   Dokument.
3. **CSP:** gebaut fuer `script-src 'self'`, ein `'unsafe-inline'` ist nicht
   noetig. Es darf **nicht** als Inline-Skript in die Seite gelegt werden — eine
   strenge CSP wuerde es blockieren. **Nonce-CSP** (`script-src 'nonce-…'`, ohne
   `'self'`): das Tag traegt das nonce der jeweiligen Antwort,
   `<script src="/static/mn-sub-nav.js" nonce="…" defer></script>`; ohne das
   Attribut blockiert der Browser die Datei.

Das Skript scrollt ausschliesslich `.mn-sub-nav__inner` (`scrollLeft`), nie die
Seite und keine Vorfahren (kein `scrollIntoView`), ohne Animation
(`prefers-reduced-motion`-neutral), und laesst eine Leiste ohne Ueberlauf
unberuehrt. Ausfuehrlich: `README.md`, Abschnitt
"Sub-Nav: aktiven Reiter zentrieren (Skript einbinden)"; Verhalten:
`components/_patterns/sub_nav.md`.

Tests `tests/components/web/test_responsive.py` (79 statt 45): Struktur der CSS-
Regeln plus Browser-Beweise (Playwright/Chromium, optional — ohne beides
sichtbar uebersprungen): Pixelprobe am Leistenrand (Hinweis nur in Richtung
verdeckten Inhalts), aktiver Reiter im Ausschnitt (mit Gegenprobe ohne die
Property), Skript unter `script-src 'self'` (der Inline-Skript-Block wird dabei
nachweislich blockiert; Gegenprobe ohne Skript), Masthead ohne Seiten-Scroll bei
320 px fuer jeden aktiven Tier. **Nicht geprueft:** Safari (WebKit) und Firefox —
die Rueckfall-Logik ist in Chromium mit entfernter Property nachgestellt, nicht
im echten Browser.

---

## [0.14.1] — 2026-10-03

### Behoben — kein horizontaler Seiten-Scroll auf Handy-Breite (390 px)

Auf einem 390-px-Viewport liefen drei Web-Komponenten ueber den Bildschirm
und erzeugten auf jeder Seite seitlichen Scroll (gemessen im Browser:
`scrollWidth` 813 bei `clientWidth` 390). Nur CSS dieser drei Komponenten;
ab `web.layout.bp-tablet` (Desktop) ist das Aussehen pixelgleich.

- **Masthead:** Kontext-Chips (`.mn-masthead__context`) und die Tier-Zeile
  duerfen in eine zweite Zeile umbrechen (`flex-wrap: wrap`); die Pillen
  bleiben eine Zeile.
- **Sub-Nav:** unter `bp-tablet` ist die Tab-Zeile eine horizontal scrollbare
  Leiste innerhalb der Sub-Nav (`overflow-x: auto`, Tabs `flex: none` +
  `white-space: nowrap`, schmale Scrollbar). Der aktive Tab wird nicht
  automatisch ins Bild gescrollt.
- **Card-Grid:** unter `bp-tablet` hoechstens zwei, unter `bp-mobile` eine
  Spalte. Der Renderer setzt dafuer zusaetzlich `--mn-card-grid-cols-tablet`
  (`min(columns, 2)`, in Python berechnet) am Wrapper; ein Raster mit
  `columns=1` bleibt einspaltig. Aelteres Markup ohne diese Variable behaelt
  auf dem Tablet die Desktop-Spaltenzahl und wird erst auf dem Handy
  einspaltig.

Dazu `media_max_width_below(token)` in `foundation.py`: Media-Query
"strikt unter dem Breakpoint" (`639.98px`/`1023.98px`), damit ein Viewport von
genau 1024 px (iPad quer) Desktop bleibt. `render_foundation_css()` selbst ist
unveraendert (inklusive `max-width: 640px`/`1024px`). Breakpoints kommen aus den
Tokens, keine Hartwerte.

Neue Tests `tests/components/web/test_responsive.py`: CSS-Struktur plus ein
Browser-Beweis (Playwright/Chromium, optional — ohne beides wird er sichtbar
uebersprungen).

---

## [0.14.0] — 2026-07-09

### Hinzugefuegt — Chat-/Konversations-Komponenten (Twin-Chat, cld1-S57)

Vier neue Web-Komponenten fuer den owner-AMBER Twin-Chat (Welle T-3):
`chat_stream` (Nachrichtenverlauf, Nutzer/Twin-Rollen), `chat_composer`
(Eingabezeile + Senden-Aktion), `stream_cursor` (Streaming-Indikator
waehrend laufender Antwort) und `status_banner` (Verbindungs-/Fehler-
Hinweise). Dazu `chat_contracts` — Pydantic-Input-Contracts fuer alle
vier Komponenten, analog den bestehenden `_patterns`-Contracts. Additiv:
keine Bestandskomponente, kein Token und kein bestehender Contract
wurde veraendert.

---

## [0.13.0] — 2026-05-21

### Hinzugefuegt — Web-Foundation (`web.*` Token-Namespace + Masthead)

Eine kohaerente Foundation fuer den Web-Tier (Design 2026-05-21, cld1-S21,
Gemini-Gate 8,5/10). Neuer `web.*`-Token-Zweig: 7-stufige Typo-Skala
(12-33px, Anker 16px), Zeilenhoehen, Web-Schriftfamilien, Strokes in ganzen
Pixeln, Separator- + Fokus-Ring-Farben, Layout-Tokens (content-width,
page-inset, Breakpoints). Die print-orientierten Tokens (`font.size.*`,
`stroke.*` in pt) bleiben unberuehrt.

Neue Komponente `masthead` — editorialer Zwei-Reihen-Kopf — loest `top_nav`
und `brand_bar` ab. Neu: `render_foundation_css()` (responsive @media-Schicht)
und `render_initiale_css()` (Drop-Cap + Wort-Initiale). Alle acht
verbleibenden Web-Komponenten auf Foundation-Tokens re-tokenisiert: kein
ad-hoc rem/pt mehr, Fokus-Ringe vereinheitlicht, totes `--font-body`-Token
gefixt, `radius-card`-Fallback korrigiert.

### Entfernt

- `top_nav` + `brand_bar` (Komponenten, Contracts, Tests) — vom `masthead` abgeloest.

---

## [0.12.0] — 2026-05-21

### Hinzugefuegt — Schaltbare Diagramm-Palette `color.diagram.*` (claudeAI Welle-3 Farb-Harmonie)

Neue kategorische Farbpalette fuer **ungeordnete** Diagramm-Kategorien
(EAM-Schichten, Architektur-Knoten-Rollen, Skill-Typen) — bewusst getrennt von
der **geordneten** `color.category.prio-*` Skala und dem 2-poligen
`color.accent.warm`. KT-1-Entscheidung S260.

12 Hues, perzeptueller OKLCH-Ring (12 Speichen alle 30 Grad, indigo-verankert:
`diagram.indigo`-Hue = 276.97 Grad = Hue von `indigo-600` `#4F46E5`). Jede
Kategorie hat drei Slots — `base` (Linien/Rahmen/Text), `nuance` (helle
Fuellung), `dark` (Text auf Nuance). Alle 12 base-Toene WCAG-AA:
base-auf-Weiss >=3:1, base-auf-Nuance >=3:1, dark-auf-Nuance >=4.5:1.

**Schaltbar zwischen zwei Varianten** — `vivid` (gamut-relative Chroma,
lebendig, aktiver Default) und `uniform` (konstante L+C, ruhiger). Beide
Tabellen liegen als `_variant_*`-Bloecke (intern, nicht im Build-Output) in
`tokens/colors.json`; die 36 semantischen `color.diagram.<hue>.{base,nuance,dark}`-
Tokens sind Style-Dictionary-Referenzen auf die aktive Variante. Umschalten ist
ein Config-Edit (Referenz-Redirect + `_variant`-Wert), kein Refactor —
Konsumenten referenzieren nur die semantischen Keys.

### Geaendert — `color.category.*` auf Option-B Temperatur-Skala (BREAKING)

Die To-Do-Prioritaets-Farben sind von vier unverbundenen Material-Design-Toenen
auf eine **Temperatur-Skala** umgestellt (KT-1 Option B, S260): Sofort=warm-rot,
Demnaechst=warm-amber, Klaeren=kuehl-indigo, Irgendwann=neutral-grau.

Alle Werte sind jetzt Referenzen auf bestehende Marken-Tokens
(`status.error-bg`, `severity.high`, `accent.warm.soft/.text`, `indigo.100/700`,
`grey.50/500/700`) — die Prioritaets-Skala wandert damit automatisch mit der
Marke. Einziges Hex-Literal: `prio-sofort-header-text` (`#b91c1c`, Tailwind
red-700) fuer WCAG-AA Kleintext-Kontrast im Sektions-Header (5.66:1 auf bg).

**Breaking — 11 `color.category.*` Tokens entfernt:** `yellow`, `red-bg`,
`red-cb`, `yellow-bg`, `yellow-cb`, `blue-bg`, `blue-text`, `blue-cb`,
`gray-text`, `gray-cb`, `green-cb`. Neu: `prio-sofort-bg`, `prio-sofort-text`,
`prio-sofort-header-text`, `prio-demnaechst-bg`, `prio-demnaechst-text`,
`prio-klaeren-bg`, `prio-klaeren-text`, `prio-irgendwann-bg`,
`prio-irgendwann-text`, `prio-irgendwann-header-text`, `checkbox` (eine
einheitliche Checkbox-Farbe statt vier stufenspezifischer).

### Entfernt — `color.architecture.*` (BREAKING)

Die 6 `color.architecture.*` Tokens (`workflow`, `workflow-light`,
`integration`, `integration-light`, `data`, `data-light`) sind retired —
abgeloest durch `color.diagram.*`. `color.light.row-alt` und
`color.status.success-bg` bleiben (markenkonform, weiter in Verwendung).

### Hinweis

v0.11.0 hatte diese Familien als 1:1-Kopien von Material-Design-Literalen
eingefuehrt (additiv, ohne visuelle Aenderung). v0.12.0 macht den eigentlichen
Schritt: weg von Material-Adhoc, hin zu marken-verankerten, perzeptuell
konstruierten Farbskalen. Die claudeAI-Konsumenten (`pdf_layer`,
`system_doc_v2`) werden in einem separaten Schritt (Part 2-CONSUMER) auf die
neuen Token-Keys umgestellt.

## [0.11.0] — 2026-05-21

### Hinzugefuegt — Kategorie- + Architektur-Farbtokens (claudeAI Welle 3)

19 neue Farbtokens, damit der `pdf_layer` der claudeAI-PKA token-clean wird
(null hartkodierte Farben). Die Werte sind 1:1-Kopien der bislang in
`pdf_utils.py` hartkodierten Material-Design-Literale — **rein additiv, kein
visueller Unterschied**, rueckwaertskompatibel zu v0.10.0.

Neue Token-Familie `color.category.*` (13) — Kategorie- und
To-Do-Prioritaets-Farben fuer PDF-Tabellen (Aufgaben-Cockpit / Briefing):
vier Prioritaets-Familien (Sofort=red, Demnaechst=yellow, Klaeren=blue,
Irgendwann=gray) je `bg`/`text`/`cb` (Checkbox), plus `green-cb` (Projekt)
und `yellow` (Warm-Gelb Akzent-Basis).

Neue Token-Familie `color.architecture.*` (6) — Architektur-Diagramm-
Knotenfarben fuer die PDF-Visualisierung: drei Knoten-Rollen (`workflow`,
`integration`, `data`) je Fuellfarbe + helle Hintergrund-Variante. Ergaenzt
`color.viz.*` (generische Diagramm-Box-Toene) um rollensemantisch benannte
Knotenfarben.

Erweiterte Familien:

- `color.status.success-bg` (`#e8f5e9`) — Erfolg/Projekt-Hintergrund,
  Gegenstueck zu den vorhandenen `error-bg`/`warning-bg`.
- `color.light.row-alt` (`#f0f4ff`) — alternierender Tabellen-Zeilen-
  Hintergrund (heller Indigo-Tint).

`#1565c0` und `#e3f2fd` erscheinen bewusst unter zwei semantischen Keys
(`category.blue-*` und `architecture.workflow*`) — gleicher Wert, andere
Rolle, korrekt fuer ein semantisches Token-System.

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
