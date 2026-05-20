# Content-Card + Card-Grid

> Generische Inhalts-Karte (Titel + Text), optional verlinkt und tier-getoent, sowie ein responsives Card-Grid, das mehrere Content-Cards in einem Spalten-Raster anordnet.

## Anatomie

```
┌─────────────────────────┐  ┌─────────────────────────┐
│ Reisefotografie         │  │ Portraet                │  <- __title (verlinkt: <a>)
│ Eine Auswahl aus zehn   │  │ Studio- und Available-  │  <- __body
│ Jahren unterwegs.       │  │ Light-Arbeiten.         │
└─────────────────────────┘  └─────────────────────────┘
        ^ Card 1                      ^ Card 2
└───────────── mn-card-grid (--mn-card-grid-cols:N) ─────┘
```

Die Content-Card ist ein `<article>` mit einem `__title` (`<h3>`) und einem
`__body` (`<p>`). Ist `href` gesetzt, wird der Titel zu einem `<a>` und die
Card traegt `mn-content-card--linked` (cursor pointer). Ist `tier` gesetzt,
faerbt eine Tier-Modifier-Klasse die Akzent-Border.

Das Card-Grid ist ein `<div class="mn-card-grid">`, dessen Spaltenzahl ueber
die CSS-Variable `--mn-card-grid-cols` am Wrapper gesetzt wird. Es bettet
beliebig viele Content-Cards ein.

## API-Contract

`ContentCardInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `title` | `str` | min_length=1, Karten-Titel (Link-Text bei gesetztem href) |
| `body` | `str` | min_length=1, Karten-Text |
| `href` | `str \| None` | optional — gesetzt macht die Karte klickbar |
| `tier` | `WebTier \| None` | optional — Tier-Familie fuer die Akzent-Border |

`CardGridInput` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `cards` | `list[ContentCardInput]` | min_length=1 |
| `columns` | `int` | ge=1, le=4, Default 3 — landet als `--mn-card-grid-cols` |

## Verwendete Tokens

- `font.body` — Schrift von Titel und Text
- `color.light.surface` — Karten-Hintergrund
- `color.light.border` — Karten-Border (Default, ohne Tier)
- `color.light.h1` — Titelfarbe
- `color.light.text-muted` — Textfarbe
- `color.tier.<tier>.border` — Akzent-Border bei gesetztem `tier`
- `radius.card` — Karten-Eckenradius

Die Card-Grid-Spaltenzahl ist KEIN Token, sondern eine pro-Instanz gesetzte
CSS-Variable `--mn-card-grid-cols` (Wert aus `CardGridInput.columns`).

## Verhalten

- HTML-Struktur Card: `<article class="mn-content-card[ mn-content-card--{tier}][ mn-content-card--linked]">`
  mit `<h3 class="mn-content-card__title">` und `<p class="mn-content-card__body">`.
- Bei gesetztem `href`: der Titel ist `<a class="mn-content-card__link" href="...">`,
  die Card traegt zusaetzlich `mn-content-card--linked`.
- `cursor: pointer` greift ausschliesslich ueber `.mn-content-card--linked` —
  eine Card ohne `href` behaelt den Default-Cursor (Affordance-Treue).
- HTML-Struktur Grid: `<div class="mn-card-grid" style="--mn-card-grid-cols:{columns}">`
  mit eingebetteten Content-Cards.
- `title`, `body` und `href` werden per `html.escape()` (href mit `quote=True`,
  da Attribut-Kontext) XSS-sicher ausgegeben.
- `render_content_card_css()` gibt Layout + Border-Regeln fuer alle 4 Tiers aus.
- `render_card_grid_css()` setzt `grid-template-columns:
  repeat(var(--mn-card-grid-cols, 3), 1fr)` — Spaltenzahl rein ueber die
  CSS-Variable, kein Hardcode.
- `inline_css=True` von `render_card_grid_html` haengt Grid- UND Card-CSS an.

## Tier-Bezug

`tier` ist optional. Ist es gesetzt, traegt die Card `mn-content-card--{tier}`
und ihre Border-Farbe kommt aus `color.tier.<tier>.border` — eine zarte
Tier-Zuordnung der Karte (z.B. eine Atelier-Karte im Start-Bereich). Ohne
`tier` bleibt die Border neutral (`color.light.border`). Anders als Tier-Chip
oder Sub-Nav ist die Content-Card NICHT tier-gebunden — der Tier-Tint ist eine
optionale Akzent-Variante, kein Pflicht-Kontext.

## Varianten

- **Plain**: nur Titel + Text, keine Border-Akzentuierung, nicht klickbar.
- **Linked**: `href` gesetzt — Titel verlinkt, `cursor: pointer`.
- **Tier-getoent**: `tier` gesetzt — Akzent-Border in der Tier-Farbe.
- **Card-Grid**: 1-4 Spalten ueber `columns`, responsiv ueber CSS-Variable.

## Plattform-Implementierungen

- `mn_design_system/components/web/content_card.py` — HTML + CSS-Renderer
  (Content-Card + Card-Grid)
- PDF/LaTeX — nicht vorgesehen (generische Web-Inhaltskarte)

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` (UX-Welle v0.2, "Offene Punkte" — Content-Card als eigene Komponente statt kpi_card-Erweiterung)
- KPI-Card-Komponente (`kpi_card.md`) — KPI-spezifisches Gegenstueck mit Trend/Sparkline
- Tier-Chip-Komponente (`tier_chip.md`) — gemeinsamer Tier-Color-Anker
