# Tier-Chip

> Primitiv-Baustein: ein einzelnes, tier-getoentes Chip-Element. Dient als kleinste Einheit der Web-Tier-Farbsprache und wird von Brand-Bar (L2, mit Border) und Sub-Nav (L3, Background-only) wiederverwendet.

## Anatomie

```
┌──────────────┐
│  Bibliothek  │   bordered = True  (L2-Status-Chip, Brand-Bar)
└──────────────┘

   Bibliothek      bordered = False (L3-Auswahl-Chip, Sub-Nav)
```

Ein `<span>` mit tier-abhaengigem Hintergrund und Textfarbe. Optionaler 1px-Rahmen
in der Tier-Border-Farbe. Kein Icon, keine Interaktivitaet im Primitiv selbst.

## API-Contract

`TierChipInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `tier` | `WebTier` | Enum (bibliothek, atelier, kabinett, start) |
| `label` | `str` | min_length=1, sichtbarer Text |
| `bordered` | `bool` | Default True — L2-Status-Chip mit Border; False = L3-Background-only |

`WebTier` (Pydantic-Enum): `bibliothek`, `atelier`, `kabinett`, `start` — mappt
1:1 auf die `color.tier.<tier>.*`-Token-Familie.

## Verwendete Tokens

- `color.tier.<tier>.bg` — Chip-Hintergrund pro Tier
- `color.tier.<tier>.text` — Chip-Textfarbe pro Tier
- `color.tier.<tier>.border` — Rahmenfarbe bei `bordered=True`
- `radius.subtle` — Eck-Radius des Chips
- `font.body` — Schrift

## Verhalten

- HTML-Struktur: ein `<span class="mn-tier-chip mn-tier-chip--{tier}[ mn-tier-chip--bordered]">`.
- `bordered=True` → zusaetzliche Klasse `mn-tier-chip--bordered`; der Rahmen ist
  `1px solid transparent` als Basis, die tierspezifische Regel setzt `border-color`.
- `bordered=False` → keine Border-Klasse, reiner Background-Chip.
- `label` wird per `html.escape()` XSS-sicher ausgegeben.
- `render_tier_chip_css()` gibt Regeln fuer alle 4 Tiers aus.

## Tier-Bezug

Tier-abhaengige Komponente. Der `tier`-Wert waehlt die `color.tier.<tier>.*`-Familie:

| Tier | Charakter |
|---|---|
| `bibliothek` | Gruen — Wissen/Bibliothek |
| `atelier` | Amber — Atelier/Arbeit |
| `kabinett` | Rot — Kabinett/privat |
| `start` | Alias auf `bibliothek` (eigene Identitaet ohne Token-Migration spaeter moeglich) |

Die Tier-Modifier-Klasse am Wurzel-Element (`mn-tier-chip--{tier}`) traegt die
Farbvarianz; kein Inline-Hex.

## Varianten

- **Bordered** (`bordered=True`, Default): L2-Status-Chip mit Rahmen — z.B. Page-Tier
  und User-Tier in der Brand-Bar. Affordance: Info, nicht klickbar.
- **Borderless** (`bordered=False`): L3-Auswahl-Chip, Background-only — Chip-Muster
  fuer aktive Sub-Nav-Tabs.

## Plattform-Implementierungen

- `mn_design_system/components/web/tier_chip.py` — HTML + CSS-Renderer
- PDF/LaTeX — geplant bei Bedarf (Pattern-First erlaubt spaeteres Nachziehen)

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` §A4 (3-Layer-Affordance)
- `color.tier.*`-Token-Familie (UX-Welle v0.2, Gemini-Gate Punkt 1 + 3)
