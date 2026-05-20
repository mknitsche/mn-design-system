# Sub-Nav

> L3 der 3-Layer-Affordance: Auswahl-Navigation INNERHALB eines Tiers. Alle Tabs teilen den Tier-Kontext der Sub-Nav; genau ein Tab ist aktiv und traegt einen dauerhaften Chip-Look.

## Anatomie

```
┌──────────────────────────────────────────────────────────┐
│  [ Alle ]   Buecher    Notizen                             │
└──────────────────────────────────────────────────────────┘
   ^ aktiv (is-active,    ^ inaktiv (transparent,
     bg + text des Tiers)   Hover -> bg-soft)
```

`<nav>` mit Tier-Modifier-Klasse und `<a>`-Tabs. Sub-Nav-Hintergrund bleibt
weiss (Barrierefreiheit). Der aktive Tab sieht aus wie ein Tier-Chip.

## API-Contract

`SubNavInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `tier` | `WebTier` | Enum — Tier-Kontext der gesamten Sub-Nav |
| `tabs` | `list[SubNavTab]` | min_length=1 |
| `aria_label` | `str` | Default `"Bereichs-Navigation"`, min_length=1 — Landmark-Label des `<nav>` (WCAG 2.4.1) |

`SubNavTab` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `label` | `str` | min_length=1, Tab-Text |
| `href` | `str` | min_length=1, Ziel-URL |
| `active` | `bool` | Default False — genau einer sollte True sein |

## Verwendete Tokens

- `color.tier.<tier>.bg` — Hintergrund des aktiven Tabs
- `color.tier.<tier>.bg-soft` — Hover-Hintergrund inaktiver Tabs (zarter als bg)
- `color.tier.<tier>.text` — Textfarbe des aktiven Tabs
- `color.light.surface` — Sub-Nav-Hintergrund (bleibt weiss)
- `color.light.border` — untere Trennlinie
- `color.light.text` — Textfarbe inaktiver Tabs
- `radius.subtle` — Eck-Radius der Tabs
- `font.body` — Schrift

## Verhalten

- HTML-Struktur: `<nav class="mn-sub-nav mn-sub-nav--{tier}" aria-label="...">`
  mit `<a class="mn-sub-nav__tab[ is-active]" href="..."[ aria-current="page"]>`
  pro Tab (`aria-current="page"` nur am aktiven Tab).
- Inaktiver Tab: nur Text, transparenter Hintergrund.
- Hover auf inaktivem Tab: `background: var(--color-tier-{tier}-bg-soft)` —
  bg-soft-Token, kein `color-mix` im Konsumenten (Gemini-Gate Punkt 1).
- Aktiver Tab (`.is-active`): `background` + `color` aus der Tier-Familie,
  dauerhafter Chip-Look.
- `transition: background 120ms` (Spec §A5).
- `label` und `href` werden per `html.escape()` (href mit `quote=True`)
  XSS-sicher ausgegeben.
- `render_sub_nav_css()` gibt Hover- und Aktiv-Regeln fuer alle 4 Tiers aus.

### Barrierefreiheit (Spec §A6)

- `<nav>` traegt `aria-label` (Default `"Bereichs-Navigation"`, per
  `SubNavInput.aria_label` ueberschreibbar) — mehrere `<nav>` auf einer Seite
  (L1 Top-Nav + L3 Sub-Nav) muessen fuer Screenreader unterscheidbar sein
  (WCAG 2.4.1). `aria_label` wird per `html.escape()` XSS-sicher ausgegeben.
- Der aktive Tab traegt zusaetzlich `aria-current="page"` — die
  "aktiv"-Information ist damit nicht rein visuell, sondern auch fuer
  assistive Technik sichtbar.

## Tier-Bezug

Tier-abhaengig: der `tier`-Wert der `SubNavInput` gilt fuer die GESAMTE Sub-Nav
(alle Tabs sind in-tier). Die Tier-Modifier-Klasse `mn-sub-nav--{tier}` am
`<nav>`-Element steuert Hover- und Aktiv-Farben. Die Sub-Nav wechselt nie den
Tier — sie navigiert innerhalb eines Bereichs (Spec §A5: L3 = Auswahl, nicht
Tier-Wechsel; das ist L1/Top-Nav).

## Varianten

- Pro Tier eine Farbvariante (bibliothek / atelier / kabinett / start) — keine
  weiteren strukturellen Varianten, die Tab-Anzahl ist variabel (min. 1).

## Plattform-Implementierungen

- `mn_design_system/components/web/sub_nav.py` — HTML + CSS-Renderer
- PDF/LaTeX — nicht vorgesehen (Sub-Nav ist eine reine Web-Interaktion)

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` §A5 (Sub-Nav-Verhalten) + §A6 (tier-soft-Hover, Barrierefreiheit)
- Tier-Chip-Komponente (`tier_chip.md`) — der aktive Tab teilt das Chip-Muster
