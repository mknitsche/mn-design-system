# KPI-Card

> Datendichte Karte fuer eine Kennzahl mit Trend.

## Anatomie

```
┌─────────────────────────────────┐
│ DAX                             │  ← Label (label, color.h1)
│                                          22.450,12 │  ← Wert (value, color.h1)
│                                          ▲ +1,25%  │  ← Change (change, color.status.success/error)
│ ▁▂▃▅▇▇▆▄                        │  ← Sparkline (color.h2)
│ Stand: Vortag-Schluss           │  ← Caption (color.text-muted, italic)
└─────────────────────────────────┘
```

## API-Contract

`KpiCardInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `label` | `str` | min_length=1, Kicker-Text (z.B. "DAX") |
| `value` | `str` | min_length=1, formatierter Wert (z.B. "22.450,12") |
| `change_pct` | `float \| None` | optional, prozentuale Veraenderung |
| `sparkline_values` | `list[float] \| None` | optional, Zeitreihe fuer Trend-Linie |
| `caption` | `str \| None` | optional, Untertitel (z.B. "30 Tage", "Stand: 04:50") |
| `richtung` | `"hoeher" \| "niedriger" \| "neutral"` | seit 0.18.0, Default `"hoeher"` — Polaritaet: welche Bewegung ist GUT? |
| `delta_wert` | `float \| None` | seit 0.18.0, optional — absolutes Delta statt Prozent (nicht zugleich mit `change_pct`) |
| `delta_einheit` | `str` | seit 0.18.0, Default `""` — Einheit hinter dem Delta; nur mit `delta_wert` |
| `dezimalstellen` | `int` (0..6) | seit 0.18.0, Default 1 — Nachkommastellen des Deltas |

`trend_direction()`-Methode liefert `KpiTrendDirection.UP/DOWN/NEUTRAL` (aus `delta_wert`,
sonst aus `change_pct`). `wertung()` liefert `KpiWertung.GUT/SCHLECHT/NEUTRAL`: Bewegung
x Polaritaet. `delta_text()` liefert das deutsch formatierte Delta oder `None`.

## Verwendete Tokens

- `color.light.h1` — Label + Value (Indigo-900, klar)
- `color.light.h2` — Sparkline-Linie (Indigo-700)
- `color.light.text-muted` — Caption (Grey-500)
- `color.status.success` — Change positiv kraeftig (Gruen)
- `color.status.error` — Change negativ kraeftig (Rot)
- `color.viz.muted` — Change neutral / Mikro-Bewegung (Grau, |Δ|<0.5%)
- `color.indigo.50` — Card-Background (Tile-Look, vom Caller umgesetzt)
- `font.family.sans` (Geist), `font.family.sans-bold` (Geist-Bold), `font.family.italic-editorial` (SourceSerif4-Italic — Caption; `<b>` darin ist fett-kursiv)

## Varianten

- **Default**: 5 Flowables, 38mm × ca. 30mm
- **Compact**: ohne Sparkline (sparkline_values=None) → Spacer-Platzhalter
- **Tile-Reihe**: Caller arrangiert mehrere Karten mit Gap-Spalten (Briefing-Pattern)

## Verhalten

- Change-Pct mit Trend-Pfeil + Farbe (▲ gruen, ▼ rot)
- **Schwellwert (v0.4.1, S239 B5):** `abs(change_pct) < 0.5` → NEUTRAL,
  grau (`color.viz.muted`), Bullet-Punkt `•` statt Pfeil. Vorher 0.01,
  hochgezogen weil kleine Marktbewegungen visuell rot/gruen-frei bleiben
  sollen (KT-1 Briefing-Befund 30.04.). Negative Mikro-Bewegung erhaelt
  manuelles Minuszeichen vor dem Wert.
- Sparkline mit `sparkline_values` (>=2): Drawing aus `build_sparkline()`
- Sparkline ohne Werte: Spacer (Hoehe identisch)
- Deutsche Komma-Notation in Change-Display
- **Polaritaet (0.18.0):** `richtung="niedriger"` macht einen Rueckgang gut (gruen, z.B.
  Gewicht, Ruhepuls), `"neutral"` wertet nicht (alles gedaempft, z.B. Schlafdauer). Der Pfeil
  zeigt IMMER die Bewegung, die Farbe die Wertung. Default `"hoeher"` ist das Verhalten von
  0.17.0 — Ausgabe bytegleich.
- **Absolutes Delta (0.18.0):** `delta_wert` + `delta_einheit` + `dezimalstellen` ersetzen
  den Prozentwert: deutsch gesetzt („+1,2 kg", „−1,2 kg", Dezimalkomma, Tausenderpunkt ab
  1.000, Minuszeichen U+2212, geschuetztes Leerzeichen vor der Einheit), kaufmaennisch
  gerundet. Rundet das Delta auf null, steht „unverändert" (Bewegung neutral, kein Pfeil im
  PDF, ■ im Web). Prozent und Delta zugleich ist ein Fehler (Mehrdeutigkeit).
- **Web-Klassen (0.18.0):** neben `is-up`/`is-down`/`is-neutral` (Bewegung) traegt das Delta bei
  `richtung != "hoeher"` eine Wertungsklasse `is-gut`/`is-schlecht`/`is-ungewertet`, die im
  CSS NACH den Bewegungsklassen steht und deren Farbe ueberschreibt.

## Plattform-Implementierungen

- `mn_design_system/components/pdf/kpi_card.py` — ReportLab Paragraphs (5 Flowables)
- `mn_design_system/components/web/kpi-card.{tsx,css}` — geplant
- `mn_design_system/latex/kpi-card.tex` — geplant

## Referenzen

- Tufte: Sparklines (Beautiful Evidence, 2006)
- Linear / Stripe Dashboard-Patterns
