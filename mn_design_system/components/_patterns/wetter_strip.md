# Wetter-Strip

> Kompakter 3-5-Tage-Vorschau-Strip mit Symbol, Temperatur und Niederschlagswahrscheinlichkeit pro Tag, optional umrahmt von einem Erzaehl-Satz.

## Anatomie

```
Nuernberg
"Klassische Aprilwetter-Mischung mit zoegerlichem Frühling."

┌────────┬────────┬────────┬────────┐
│ Heute  │   Di   │   Mi   │   Do   │
│   ☀    │   ⛅   │   🌧   │   ⛅   │
│ 12/22  │ 10/19  │  8/14  │ 11/17  │
│ 10%    │ 30%    │ 80%    │ 20%    │
└────────┴────────┴────────┴────────┘
```

3-5 Tageskacheln nebeneinander. Erste Kachel zeigt "Heute", folgende
Wochentag-Abkuerzungen. Symbol oben, Temperatur Min/Max, Niederschlag-%.

Optional: ein Erzaehl-Satz oberhalb (z.B. von Wetterochs-Mail) im Italic-Stil.

## API-Contract

`WetterStripInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `days` | `list[WetterDay]` | min_length=3, max_length=5 |
| `summary_text` | `str \| None` | optional Erzaehl-Satz |
| `location` | `str` | min_length=1, Header-Text |

`WetterDay` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `header_label` | `str` | min_length=1, max_length=15 |
| `category` | `WetterCategory` | Enum (sonnig, heiter, bewoelkt, regen, ...) |
| `temp_min_c` | `int` | (Celsius) |
| `temp_max_c` | `int` | (Celsius) |
| `precip_pct` | `int` | 0-100 |

## Verwendete Tokens

- `font.body` — Tageskachel-Zahlen
- `font.italic` — Erzaehl-Satz
- `color.light.h2` — Symbol-Farbe (Phosphor)
- `color.light.text-muted` — Niederschlag-%
- `space.2` — innere Padding der Kacheln
- `radius.card` — optional Kachel-Border

## Verhalten

- Symbol-Mapping: `WetterCategory` → Phosphor-Codepoint
  - sonnig → `sun` (U+E472)
  - heiter → `cloud-sun` (U+E540)
  - bewoelkt → `cloud` (U+E1AA)
  - regen → `cloud-rain` (U+E1B4)
  - schnee → `cloud-snow` (U+E1B8)
  - gewitter → `lightning` (U+E2DE)
  - nebel → `cloud-fog` (U+E53C)
  - wind → `wind` (U+E5D2)
- Temperatur-Format: `"{min}/{max}"` (Bindestrich entfernt zugunsten Slash)
- Niederschlag-Suffix: `"{precip}%"`

## Varianten

- **Default**: 4 Tage mit Erzaehl-Satz
- **Compact**: 3 Tage, kein Erzaehl-Satz
- **Extended**: 5 Tage mit Erzaehl-Satz, fuer Wochenend-Wetter

## Plattform-Implementierungen

- `mn_design_system/components/pdf/wetter_strip.py` — ReportLab `Table`
- `mn_design_system/components/web/wetter-strip.{tsx,css}` — geplant
- `mn_design_system/components/latex/wetter-strip.tex` — geplant

## Referenzen

- Apple iOS Wetter-App (Strip-Layout)
- Wetter.com / DWD-OpenData Wochenuebersicht
