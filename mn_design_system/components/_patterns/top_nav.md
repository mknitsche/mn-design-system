# Top-Nav

> L1 der 3-Layer-Affordance: Tier-Wechsel-Navigation. Transparente Pills auf dunklem Grund; jeder Eintrag fuehrt in einen anderen Tier. Genau ein Eintrag ist aktiv und traegt einen Tier-Color-Tint.

## Anatomie

```
┌──────────────────────────────────────────────────────────┐  dunkler Grund
│  ( Start )   Bibliothek    Atelier    Kabinett             │
└──────────────────────────────────────────────────────────┘
   ^ aktiv (is-active,      ^ inaktiv (transparent,
     tier-color-tint)        Hover -> weiss-tint)
```

`<nav>` mit `<a>`-Pills. Hintergrund ist dunkel (`color.dark.surface`). Der
aktive Eintrag traegt den `bg`/`text`-Tint seiner Tier-Familie, alle anderen
sind transparente Pills mit hellem Text.

## API-Contract

`TopNavInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `items` | `list[TopNavItem]` | min_length=1 |
| `aria_label` | `str` | Default `"Hauptnavigation"`, min_length=1 — Landmark-Label des `<nav>` (WCAG 2.4.1) |

`TopNavItem` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `label` | `str` | min_length=1, Eintrags-Text |
| `href` | `str` | min_length=1, Ziel-URL (Tier-Einstieg) |
| `tier` | `WebTier` | Enum — Ziel-Tier dieses Eintrags |
| `active` | `bool` | Default False — genau einer sollte True sein |

## Verwendete Tokens

- `color.dark.surface` — dunkler Hintergrund der Top-Nav
- `color.dark.text` — Textfarbe inaktiver Pills
- `color.tier.<tier>.bg` — Hintergrund des aktiven Eintrags
- `color.tier.<tier>.text` — Textfarbe des aktiven Eintrags
- `radius.round` — Pill-Radius
- `font.body` — Schrift

Hover-Tint inaktiver Pills ist `rgba(255,255,255,0.08)` — bewusst neutral
(weiss), kein Token: die Top-Nav wechselt UEBER die Tier, ein Tier-Tint waere
beim Hover irrefuehrend (Spec §A4).

## Verhalten

- HTML-Struktur: `<nav class="mn-top-nav" aria-label="...">` mit
  `<a class="mn-top-nav__item mn-top-nav__item--{tier}[ is-active]" href="..."[ aria-current="page"]>`
  pro Eintrag (`aria-current="page"` nur am aktiven Eintrag).
- Inaktiver Eintrag: transparente Pill, heller Text.
- Hover auf inaktivem Eintrag: weiss-Tint (`rgba(255,255,255,0.08)`) — neutral,
  weil die Top-Nav ueber-tier wechselt (Spec §A4).
- Aktiver Eintrag (`.is-active`): `background` + `color` aus der Ziel-Tier-Familie,
  damit der aktuelle Tier sichtbar ist.
- `transition: background 120ms`.
- `label`, `href` und `aria_label` werden per `html.escape()` (href + aria_label
  mit `quote=True`) XSS-sicher ausgegeben.
- `render_top_nav_css()` gibt Layout + Aktiv-Regeln fuer alle 4 Tiers aus.

### Barrierefreiheit (Spec §A6 / WCAG 2.4.1)

- `<nav>` traegt `aria-label` (Default `"Hauptnavigation"`, per
  `TopNavInput.aria_label` ueberschreibbar) — mehrere `<nav>` auf einer Seite
  (L1 Top-Nav + L3 Sub-Nav) muessen fuer Screenreader unterscheidbar sein.
- Der aktive Eintrag traegt zusaetzlich `aria-current="page"` — die
  "aktiv"-Information ist damit nicht rein visuell, sondern auch fuer
  assistive Technik sichtbar.

## Tier-Bezug

Tier-abhaengig pro Eintrag: jeder `TopNavItem` traegt sein eigenes Ziel-`tier`.
Die Tier-Modifier-Klasse `mn-top-nav__item--{tier}` greift nur im
`is-active`-Zustand — der aktive Eintrag zeigt den Tier-Color-Tint seines
Ziel-Tiers. Im Unterschied zur Sub-Nav (L3, in-tier) wechselt die Top-Nav den
Tier (Spec §A4: L1 = Tier-Wechsel).

## Varianten

- Pro Eintrag eine Ziel-Tier-Variante (bibliothek / atelier / kabinett / start)
  — keine weiteren strukturellen Varianten, die Eintrags-Anzahl ist variabel
  (min. 1).

## Plattform-Implementierungen

- `mn_design_system/components/web/top_nav.py` — HTML + CSS-Renderer
- PDF/LaTeX — nicht vorgesehen (Top-Nav ist eine reine Web-Interaktion)

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` §A4 (3-Layer-Affordance, L1 Top-Nav)
- Sub-Nav-Komponente (`sub_nav.md`) — L3-Gegenstueck, in-tier statt ueber-tier
- Tier-Chip-Komponente (`tier_chip.md`) — gemeinsamer Tier-Color-Anker
