# News-Item

> Kaskaden-Einheit der Briefing-Web-Ausgabe (Welle 3): Rang + Schlagzeile
> (optional interner "tiefer"-Link) + Basis-Text + Meta-Zeile (Kategorie · Zeit ·
> Quelle) + optionaler aufklappbarer Vertiefungs-Stufe ("+ mehr"). Der Aufmacher
> ist dezent prominent (Top-Akzentlinie + groesserer Titel — Tufte).

## Anatomie

```
┌─ 01 ── Aufmacher · stand auf S1 ──────────────────────────────┐  (eyebrow optional)
│        EU-Kommission warnt: US-Exportkontrollen …            │  (Titel, optional Link)
│        Bruessel reagiert auf den US-Exklusivzugang …          │  (Basis-Text)
│        POLITIK   vor 3 Std   Quelle: euronews.com ↗           │  (Meta-Zeile)
│        + mehr (medium)                                        │  (<summary>, optional)
│        │ MEDIUM · LAGEBERICHT                                 │  (Detail, aufgeklappt)
│        │ Die Kommission prueft eine Reaktion …               │
│        │ Quelle: euronews.com ↗ · weitere: heise.de ↗        │
└───────────────────────────────────────────────────────────────┘
```

`<article class="mn-news-item">` → `__row` → (`__rank`? + `__body` → (`__eyebrow`? ·
`__title`[·`__title-link`] · `__text` · `__meta` · `<details>`?)). Der Aufmacher
traegt zusaetzlich `mn-news-item--aufmacher`.

## API-Contract

`NewsItemInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `rank` | `str \| None` | Default None — Reihungs-Marker ("01" / "★") |
| `eyebrow` | `str \| None` | Default None — Augenbrauen-Zeile |
| `is_aufmacher` | `bool` | Default False — Aufmacher-Modifier |
| `title` | `str` | min_length=1 — Schlagzeile |
| `deeper_href` | `str \| None` | Default None — interner "tiefer"-Link auf dem Titel |
| `text` | `str` | min_length=1 — Basis-Tiefe |
| `kategorie` | `str` | min_length=1 — Sektions-Etikett (Meta) |
| `zeitangabe` | `str` | min_length=1 — relative Zeit (Meta) |
| `source` | `SourceRefInput \| None` | Default None — primaere Quelle (Meta) |
| `detail` | `NewsItemDetail \| None` | Default None — die "+ mehr"-Stufe |

`NewsItemDetail` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `level_label` | `str` | min_length=1 — Tiefen-Etikett ("Medium · Lagebericht") |
| `text` | `str` | min_length=1 — vertiefender Text |
| `sources` | `SourceRefInput \| None` | Default None — Quelle(n) der Vertiefung |
| `summary_label` | `str` | Default "mehr", min_length=1 — Klammer-Wort in "+ mehr (…)" |

## Verwendete Tokens

- `web.text.lead` / `web.text.h3` — Titel (Basis / Aufmacher)
- `web.text.body` — Basis- und Detail-Text · `web.text.ui` — Rang, Summary
- `web.text.caption` — Meta-Zeile, Eyebrow, Level-Label
- `web.leading.h3` / `web.leading.h2` / `web.leading.body` — Zeilenhoehen
- `color.light.h1` — Titel · `color.light.h2` — Kategorie · `color.grey.700` — Text
- `color.light.accent` — Eyebrow, Summary, Level, Aufmacher-Linie, Title-Hover
- `color.light.accent-soft` — Detail-Border-left · `color.grey.300` — Rang
- `color.light.surface-subtle` — Item-Trennlinie (border-bottom)
- `web.stroke.line` / `web.stroke.line-strong` / `web.stroke.focus` — Linien
- `space.1` / `space.2` / `space.3` / `space.4` — Abstaende

## Verhalten

- `rank=None` → kein Rang-Span. `eyebrow=None` → keine Eyebrow-Zeile.
- `deeper_href` gesetzt → Titel wird zum internen `<a class="mn-news-item__title-link">`;
  sonst Klartext. Nur der Titel ist verlinkt (kein Stretched-Link — die Meta-Zeile
  und der Expander tragen eigene Interaktion).
- `is_aufmacher=True` → `mn-news-item--aufmacher` (Top-Akzentlinie + groesserer Titel).
- Meta-Zeile rendert immer Kategorie + Zeit; `source` (falls gesetzt) wird ueber
  die source_ref-Komponente inline angehaengt.
- `detail=None` → KEIN `<details>`-Expander. Sonst `<summary>+ mehr (summary_label)</summary>`
  + Level-Label + Detail-Text + (falls gesetzt) Detail-Quelle ueber source_ref.
  Der native Disclosure-Marker wird ausgeblendet (`list-style:none` +
  `::-webkit-details-marker`).
- Alle Inhalte werden per `html.escape()` XSS-sicher ausgegeben; hrefs zusaetzlich
  mit `quote=True`.
- Title-Link hat einen Token-basierten `:focus-visible`-Indikator (WCAG 2.4.7).
- `render_news_item_html(input, inline_css=True)` haengt News-Item- UND
  Source-Ref-CSS an.

## Varianten

- **TOP-Seite ("S1")**: kurzer `text`, `deeper_href` auf das Themenfeld-Item,
  `detail.summary_label="medium"`.
- **Themenfeld**: medium `text`, `detail.summary_label="detailliert"`; das auf S1
  gereihte Item zusaetzlich `is_aufmacher=True` + `eyebrow="Aufmacher · stand auf S1"`
  + `rank="★"`.
- **Ohne Vertiefung**: `detail=None` (kein Expander).

## Plattform-Implementierungen

- `mn_design_system/components/web/news_item.py` — HTML- + CSS-Renderer
- PDF/LaTeX — nicht implementiert (Pattern-First erlaubt spaeteres Nachziehen).

## Referenzen

- Mockup: `claudeAI ~/sync/build-artifacts/2026-06-14-briefing-web-mockup.html`
  (`.item`, `.item--aufmacher`, `.item__row/__rank/__body/__title/__text/__detail/__sources`,
  `.eyebrow`, `.meta/.cat`, `<details>`-Muster).
- Baustein: nutzt `source_ref.md` fuer `source` und `detail.sources`.
