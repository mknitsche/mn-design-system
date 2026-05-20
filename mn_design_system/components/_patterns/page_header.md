# Page-Header

> Seiten-Kopf einer mkn-desk.com-Seite: ein H1-Titel und ein optionaler Lead-Absatz. Tier-neutral — kein Tier-Bezug, auf jeder Seite identisch aufgebaut.

## Anatomie

```
┌──────────────────────────────────────────────────────────┐
│  Bibliothek                                                │  <- h1
│  Buecher, Notizen und gesammeltes Wissen.                  │  <- Lead (optional)
└──────────────────────────────────────────────────────────┘
```

`<header>` mit `<h1>` und — falls gesetzt — einem `<p>`-Lead. Reiner
Inhalts-Kopf, keine Navigation und keine Interaktion.

## API-Contract

`PageHeaderInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `title` | `str` | min_length=1, H1-Text |
| `lead` | `str \| None` | Default None — optionaler Lead-Absatz |

## Verwendete Tokens

- `color.light.h1` — Farbe des H1-Titels
- `color.light.text-muted` — Farbe des Lead-Absatzes
- `font.body` — Schrift

Schriftgroessen sind in `rem` direkt im Komponenten-CSS gesetzt, nicht ueber
`var(--font-size-*)`: die `font.size.*`-Tokens sind print-orientiert (pt). Web
nutzt rem — konsistent mit den bestehenden Web-Renderern (kpi_card,
wetter_strip).

## Verhalten

- HTML-Struktur: `<header class="mn-page-header">` mit
  `<h1 class="mn-page-header__title">` und optionalem
  `<p class="mn-page-header__lead">`.
- `lead` wird nur gerendert, wenn gesetzt (nicht `None`).
- `title` und `lead` werden per `html.escape()` XSS-sicher ausgegeben.
- `render_page_header_css()` liefert Layout + Farben fuer Titel und Lead.

## Varianten

- Mit Lead / ohne Lead — die einzige strukturelle Variante. Keine Tier-,
  Groessen- oder Farbvarianten (Page-Header ist tier-neutral).

## Plattform-Implementierungen

- `mn_design_system/components/web/page_header.py` — HTML + CSS-Renderer
- PDF/LaTeX — nicht in Welle A; ein PDF-Pendant kann spaeter folgen
  (Pattern-First erlaubt das).

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` §Welle A (Page-Header — Contract `PageHeaderInput` h1 + Lead)
