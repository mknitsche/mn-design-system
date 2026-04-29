# KPI-Card

> Datendichte Karte für eine Kennzahl mit Trend.

## Anatomie

```
┌─────────────────────────────────┐
│ LABEL          (mono kicker)    │  ← font.caption, color.text-muted, tracking.extra
│                                 │
│ 1.234,56       (display value)  │  ← font.h1, color.h1
│ EUR / Quartal  (caption)        │  ← font.caption, color.text-muted
│                                 │
│ ▁▂▃▅▇▇▆▄    +12,4%             │  ← Sparkline + Delta-Indikator
└─────────────────────────────────┘
```

## Verwendete Tokens

- `font.size.caption`, `font.size.h1`
- `color.light.h1`, `color.light.text-muted`, `color.status.success` (Delta positiv) / `color.status.error` (negativ)
- `space.4` (Card-Padding), `space.2` (innere Gaps)
- `radius.card` oder `radius.none` (Tufte-Default)
- `stroke.hairline` (Card-Border, optional)

## Varianten

- **Default**: Card mit `stroke.hairline` Border
- **Compact**: Halbe Padding (`space.2`), kein Border, fuer Dashboard-Reihen
- **Highlight**: BG `color.indigo.50`, fuer Hervorhebung

## Verhalten

- Sparkline rendert Zeitreihe (typisch 7-30 Punkte)
- Delta-Indikator: Pfeil-up (`▲` oder Phosphor `caret-up`) bei positiv, sonst `▼`
- Bei Hover (Web): leichter Schatten `shadow.subtle`

## Plattform-Implementierungen

- `components/python/kpi_card.py` — ReportLab Flowable
- `components/web/kpi-card.css` + `kpi-card.html` — Custom Element / React
- `components/typescript/KpiCard.tsx` — React-Component (folgt mit claude-design)

## Referenzen

- Tufte: Sparklines (Beautiful Evidence, 2006)
- Linear/Stripe Dashboard-Patterns
