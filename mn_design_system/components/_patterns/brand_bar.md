# Brand-Bar

> L2 der 3-Layer-Affordance: Brand-Text plus 0-3 tier-getoente Status-Chips (z.B. Page-Tier + User-Tier). Affordance Info — die Bar selbst ist nicht klickbar, die Chips zeigen Kontext.

## Anatomie

```
┌──────────────────────────────────────────────────────────┐
│  mkn-desk                  [ Bibliothek ]  [ Owner ]       │
└──────────────────────────────────────────────────────────┘
   ^ Brand-Text                ^ Status-Chips (bordered, L2)
```

`<header>` mit Brand-Text links und einem Chip-Container rechts (Flex,
space-between). Die Chips sind bordered Tier-Chips. Bei leerer Chip-Liste bleibt
nur der Brand-Text.

## API-Contract

`BrandBarInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `brand_text` | `str` | min_length=1, Brand-Schriftzug |
| `chips` | `list[BrandBarChip]` | default leer, max_length=3 |

`BrandBarChip` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `tier` | `WebTier` | Enum (bibliothek, atelier, kabinett, start) |
| `label` | `str` | min_length=1, Chip-Text |

## Verwendete Tokens

- `color.light.surface` — Bar-Hintergrund
- `color.light.border` — untere Trennlinie
- `color.light.h1` — Brand-Text-Farbe
- `color.tier.<tier>.*` — pro Chip (via eingebetteten Tier-Chip)
- `font.body` — Schrift

## Verhalten

- HTML-Struktur: `<header class="mn-brand-bar">` mit `mn-brand-bar__brand` und
  `mn-brand-bar__chips`.
- Jeder Chip wird ueber `render_tier_chip_html(TierChipInput(..., bordered=True))`
  eingebettet — Tier-Chip-Wiederverwendung, kein doppelter Renderer.
- `brand_text` wird per `html.escape()` XSS-sicher ausgegeben; Chip-Labels
  escaped der Tier-Chip-Renderer.
- Leere `chips`-Liste rendert valide (nur Brand-Text).
- `inline_css=True` gibt Brand-Bar-CSS UND Tier-Chip-CSS aus, da Chips
  eingebettet sind.

## Tier-Bezug

Tier-abhaengig ueber die eingebetteten Chips: jeder `BrandBarChip.tier` waehlt
die `color.tier.<tier>.*`-Familie. Typische Belegung: ein Chip fuer den
Page-Tier (welcher Bereich), ein Chip fuer den User-Tier (Berechtigungsstufe).
Die Bar selbst ist tier-neutral (heller Surface-Hintergrund).

## Varianten

- **Mit Chips** (Default): Brand-Text + 1-3 Status-Chips.
- **Ohne Chips**: nur Brand-Text — z.B. Public-Landing ohne Tier-Kontext.

## Plattform-Implementierungen

- `mn_design_system/components/web/brand_bar.py` — HTML + CSS-Renderer
- PDF/LaTeX — geplant bei Bedarf

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` §A4 (3-Layer-Affordance, L2)
- Tier-Chip-Komponente (`tier_chip.md`)
