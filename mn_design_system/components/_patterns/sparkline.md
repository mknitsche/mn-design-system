# Sparkline

> Datendichte Mini-Visualisierung einer Zeitreihe ohne Achsen — Tufte-Style.

## Anatomie

```
       ▁▂▃▅▇▇▆▄
       └────────┘
       28 mm × 8 mm
```

Eine durchgehende Linie ohne Beschriftung, ohne Achsen, ohne Tick-Marks.
Position: meist als Inline-Annotation neben Wert oder als Trend in einer
KPI-Karte. Lesegeschwindigkeit ist primaer; Praezision sekundaer.

## API-Contract

`SparklineInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `values` | `list[float]` | min_length=2, chronologisch (alt -> neu) |
| `width` | `float` | > 0, in Points (z.B. 28 * mm) |
| `height` | `float` | > 0, in Points (z.B. 8 * mm) |
| `color` | `str \| None` | optional Hex-String, None = Default-H2 |

Implementierung: `build_sparkline(input: SparklineInput) -> Drawing` (PDF) bzw.
HTML-Element (web).

## Verwendete Tokens

- `color.light.h2` — Default-Linienfarbe (Indigo-700)
- `stroke.hairline` — Linienstaerke (0.6 pt heute, kann ueber Token gesetzt werden)

## Verhalten / Skala

Adaptive Skalierung (Default-Heuristik):
- **±10% vom letzten Wert** als Standard-Skala
- **±5%** bei sehr ruhigen Werten (val_range < 5%)
- **Auto-Aufweitung** wenn Range > ±10%

So bleiben Bewegungen sichtbar, aber Mikro-Rauschen wird nicht als grosse
Volatilitaet dargestellt.

## Varianten

- **Default**: Line, 0.6 pt, color H2
- **Inline-Mini**: kleinere Hoehe (4mm), hauptsaechlich neben Inline-Text
- **Trend-only**: nur erster + letzter Wert farbig markiert (Welle E)

## Plattform-Implementierungen

- `mn_design_system/components/pdf/sparkline.py` — ReportLab `Drawing` mit `PolyLine`
- `mn_design_system/components/web/sparkline.{tsx,html}` — geplant
- `mn_design_system/components/latex/sparkline.tex` — geplant (TikZ)

## Referenzen

- Tufte: *Beautiful Evidence* (2006), Kapitel "Sparklines"
- Edward Tufte's "data-ink ratio" als Leitprinzip
