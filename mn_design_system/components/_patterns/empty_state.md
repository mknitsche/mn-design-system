# Empty-State

> Ruhiger Leer-Zustand-Block: ein zurueckhaltender Hinweis "hier erscheint bald etwas". Kein Baustellen-Schild, kein greller Kasten — gedaempfter Text auf zarter Flaeche, optional tier-verankert.

## Anatomie

```
┌────────────────────────────────────────────┐
│                                            │  border-left 3px (neutral
│  Sobald Eintraege da sind, erscheinen      │  oder tier-getoent)
│  sie hier.                                 │
│                                            │
└────────────────────────────────────────────┘
```

Ein `<div>` mit zarter Hintergrundflaeche und linkem Akzentstrich. Darin ein
einzelner `<p>` mit dem gedaempften Hinweistext. Kein Icon, keine Interaktivitaet,
keine Ueberschrift — der Block ist bewusst leise.

## API-Contract

`EmptyStateInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `message` | `str` | min_length=1, sichtbarer Hinweistext |
| `tier` | `WebTier \| None` | Default None — optionale Tier-Familie fuer eine zarte farbliche Verankerung |

`WebTier` (Pydantic-Enum): `bibliothek`, `atelier`, `kabinett`, `start` — mappt
1:1 auf die `color.tier.<tier>.*`-Token-Familie.

## Verwendete Tokens

- `color.light.surface-subtle` — Hintergrund des Blocks
- `color.light.border` — Akzentstrich-Farbe ohne Tier
- `color.light.text-muted` — Farbe des Hinweistexts
- `color.tier.<tier>.border` — Akzentstrich-Farbe bei gesetztem `tier`
- `radius.subtle` — Eck-Radius
- `font.body` — Schrift

## Verhalten

- HTML-Struktur: ein `<div class="mn-empty-state[ mn-empty-state--{tier}]">` mit
  einem `<p class="mn-empty-state__message">`.
- `tier=None` → keine Tier-Modifier-Klasse; der Akzentstrich bleibt neutral
  (`color.light.border`).
- `tier` gesetzt → zusaetzliche Klasse `mn-empty-state--{tier}`; die tierspezifische
  Regel ueberschreibt `border-left-color` mit der Tier-Border-Farbe.
- `message` wird per `html.escape()` XSS-sicher ausgegeben.
- `render_empty_state_css()` gibt die Basis-Regel plus Modifier-Regeln fuer alle
  4 Tiers aus.
- `inline_css=True` haengt das Komponenten-CSS in einem `<style>`-Block an —
  fuer Single-Snippet-Embeds.

## Tier-Bezug

Optional tier-abhaengig. Ohne `tier` ist der Block tier-neutral. Mit `tier` waehlt
der Wert die `color.tier.<tier>.border`-Farbe fuer den linken Akzentstrich — eine
zarte Verankerung im jeweiligen Web-Bereich:

| Tier | Charakter |
|---|---|
| `bibliothek` | Gruen — Wissen/Bibliothek |
| `atelier` | Amber — Atelier/Arbeit |
| `kabinett` | Rot — Kabinett/privat |
| `start` | Alias auf `bibliothek` (eigene Identitaet ohne Token-Migration spaeter moeglich) |

Die Tier-Modifier-Klasse am Wurzel-Element (`mn-empty-state--{tier}`) traegt die
Farbvarianz; kein Inline-Hex.

## Varianten

- **Neutral** (`tier=None`, Default): tier-loser Leer-Zustand — der Akzentstrich
  nutzt `color.light.border`. Fuer bereichsuebergreifende Kontexte.
- **Tier-verankert** (`tier` gesetzt): der Akzentstrich uebernimmt die Tier-Farbe —
  z.B. auf einer Atelier- oder Bibliothek-Bereichsseite.

## Plattform-Implementierungen

- `mn_design_system/components/web/empty_state.py` — HTML + CSS-Renderer
- PDF/LaTeX — geplant bei Bedarf (Pattern-First erlaubt spaeteres Nachziehen;
  mkn-desk.com hat keinen PDF-Export von Web-Seiten, daher kein Absturz-Pfad)

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-20-ux-welle-b-design.md` Phase 1.3
- `color.tier.*`-Token-Familie (UX-Welle v0.2)
