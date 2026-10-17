# Verlauf-Chart

> Zeitreihen-Diagramm mit Zielband, Ereignis-Marken und Zoom — auf Apache ECharts,
> selbst gehostet, Farben ausschliesslich aus den Tokens.

## Anatomie

```
 kg                                         ── Waage  ┄┄ 7-Tage-Mittel
 83 ┤      ╭╮                                   (Legende nur bei > 1 Reihe)
 81 ┤▒▒▒▒▒▒▒▒╲▒▒▒▒▒▒▒▒▒▒╲▒▒▒▒▒▒▒▒  ← Zielband (markArea)
 79 ┤        ╲╱          ╲╱    ┆ ← Ereignis-Marke (markLine)
    └──────────────────────────
      01.08.   01.09.   01.10.
    ▐█████████████████████████▌  ← Zoom-Leiste (dataZoom slider)
 Waage · 7-Tage-Mittel (gestrichelt). Zielband 78–81 kg
```

## API-Contract

`VerlaufChartInput` (Pydantic, `contracts.py`; frozen, `extra=forbid`):

| Feld | Typ | Constraint |
|---|---|---|
| `titel` | `str` | 1..80 |
| `einheit` | `str` | 0..16, Einheit der Werteachse |
| `reihen` | `list[VerlaufReihe]` | 1..4; die erste liegt auf der linken Achse (sie traegt Zielband, Marken, Beschreibung) |
| `von`, `bis` | `date` | `von < bis`; ganze Tage, `bis` einschliesslich |
| `zielband_min`, `zielband_max` | `float \| None` | beide oder keins, `min <= max` |
| `markierungen` | `list[VerlaufMarkierung]` | max. 12 |
| `dezimalstellen` | `int` | 0..3 (Achse, Tooltip) |
| `hoehe` | `Literal[180, 220, 260, 320, 400, 600]` | CSS-Klasse je Stufe, nie `style=` |
| `beschreibung` | `str \| None` | aria-label; Default `beschreibung_text()` |

`VerlaufReihe`: `label` (1..40), `punkte` (darf leer sein), `art` (`messung` =
durchgezogen, `gleitend` = gestrichelt, ohne Symbole), `achse` (`links` = Default,
`rechts` = zweite Werteachse, seit 0.17.1). `VerlaufPunkt`: `t`
(`date` oder `datetime`; ein `datetime` ohne Zone gilt als Europe/Berlin), `wert`
(endlich — NaN/Infinity sind in JSON nicht darstellbar). `VerlaufMarkierung`: `t`,
`label` (1..30).

## Funktionen (`components/web/verlauf_chart.py`)

| Funktion | Liefert |
|---|---|
| `verlauf_chart_option(input)` | ECharts-Option als reines JSON — keine Farbe, keine Funktion |
| `render_verlauf_chart_html(input, kennung=…)` | `<figure>` mit Flaeche, Datenblock `<kennung>-daten`, Textlegende |
| `echarts_theme("hell" \| "dunkel")` | Theme aus den Tokens |
| `render_verlauf_chart_js()` | Loader (registriert beide Themes, startet jede Figur) |
| `render_verlauf_chart_css()` | Layout, sechs Hoehenklassen, Legende |

## Einbindung beim Konsumenten (CSP `script-src 'self'`)

1. `web.vendor_js_dir() / web.ECHARTS_DATEI` unter dem versionierten Namen
   `echarts-<ECHARTS_VERSION>.min.js` ausliefern; LICENSE, NOTICE und
   `licenses/LICENSE-d3` aus demselben Ordner mitgeben (Apache-2.0; der Build
   enthaelt d3.js-Code unter BSD-3, dessen Lizenztext mitgehen muss).
2. `render_verlauf_chart_js()` als eigene Datei ausliefern.
3. Beide als `<script src="…" defer>` einbinden, Bibliothek zuerst. Unter einer
   Nonce-CSP traegt jedes Tag das Nonce der Antwort. NIE inline.
4. `render_verlauf_chart_css()` in das Seiten-CSS aufnehmen.
5. Unter jedes Diagramm eine server-gerenderte Tabelle der Werte legen: ohne
   JavaScript (oder ohne Bibliothek) bleibt sie die Darstellung — der Loader
   beendet sich dann still.

## Verhalten

- **Zeitfenster:** Punkte ausserhalb von `von`..`bis` (ganze Tage) werden nicht gezeichnet;
  die Zeitachse steht auch ohne Punkte. Zeitpunkte erscheinen als Berliner Wanduhr.
- **Leeres Fenster:** Achse plus Hinweis „keine Werte im Fenster", kein Zoom.
- **Zielband:** Mit Zielband erhaelt die Werteachse feste, runde Grenzen, damit ein Band
  ausserhalb der Daten nicht abgeschnitten wird.
- **Zielband-Beschriftung:** unter dem Diagramm ohne ueberfluessige Nullen und deutsch:
  „Zielband 70–74 kg", „72,5–74 kg", „1.000–1.500 kcal"; ein negativer Wert traegt das
  Minuszeichen U+2212. Die Nachkommastellen sind `dezimalstellen`, gekuerzt wird nur,
  was hinter dem Komma nur aus Nullen besteht.
- **Zweite Werteachse (0.17.1):** liegt mindestens eine Reihe auf `achse="rechts"`
  (z.B. 7-Tage-Summen neben Tageswerten), ist `yAxis` der Option eine Liste aus linker
  und rechter Achse, die rechten Reihen zeigen mit `yAxisIndex: 1` auf die rechte.
  Beide Achsen tragen dieselbe Einheit (`einheit`) und dieselbe Zahlenschreibweise; die
  rechte hat eine freie Skala und kein Gitter, der rechte Rand wird auf 48 px verbreitert.
  Zielband und feste Achsengrenzen gelten nur fuer die linke Achse und richten sich nur
  nach den linken Reihen. Ohne rechte Reihe bleibt `yAxis` ein einzelnes Objekt — die
  Option ist dann dieselbe wie in 0.17.0. Die Textlegende nennt „(rechte Achse)".
- **Zoom:** ziehen/pinch (inside) und Leiste; das Mausrad zoomt nur mit Strg, damit die
  Seite unter dem Zeiger weiter scrollt. `touch-action: pan-y` laesst die Seite
  senkrecht scrollen.
- **Zahlen und Daten:** deutsch (`Intl`, Komma, Tausenderpunkt) durch den Loader aus
  `data-dezimalstellen` und der Einheit; die Option bleibt reines JSON.
- **Barrierefreiheit:** `role="img"` mit `aria-label` (Letztstand, Zeitraum), Legende als
  Text unter dem Diagramm, Achsentext mit AA-Kontrast; `prefers-reduced-motion` schaltet
  die Animation ab.

## Verwendete Tokens

- Reihen: `color.diagram.{indigo,teal,amber,azure}.base`
- Text/Achsen: `color.{light,dark}.text-muted`, Gitter `color.grey.200` / `color.dark.border`
- Zielband: `color.status.success-bg` (hell), `color.status.success` mit Deckkraft (dunkel)
- Zoom-Leiste: `color.{light,dark}.accent`, `accent-soft`
- Schrift: `web.font.sans` (`css_font_stack`), Groesse `web.text.caption`

## Plattform-Implementierungen

- `mn_design_system/components/web/verlauf_chart.py` + `vendor/echarts/` — Web (diese Spec)
- PDF: nicht vorgesehen (dort `sparkline`/`kpi_card`)
