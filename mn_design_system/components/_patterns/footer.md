# Footer

> Schlanke einzeilige Seiten-Fusszeile von mkn-desk.com: links eine
> Identitaets-Zeile aus `|`-getrennten Segmenten, rechts die Rechtslinks
> (`·`-getrennt) plus optionale Version. Tier-neutral — auf jeder Seite identisch.

## Anatomie

```
───────────────────────────────────────────────────────────  <- Hochstrich (border-top)
 mkn-desk.com | Atelier · AMBER | Profil   Impressum · Datenschutz · v0.2.1
```

`<footer>` mit einer flex-Zeile (`mn-footer__inner`, `justify-content: space-between`):

- **links** `mn-footer__identity` — Identitaets-Segmente, mit `|`-Strich getrennt.
  Ein Segment kann ein client-seitig gefuellter Hydration-Slot sein (z.B. Profil).
- **rechts** `mn-footer__meta` — Rechtslinks, mit `·` getrennt, optional gefolgt
  von der Version (dezent).

Die "Hochstrich"-Trennlinie ueber dem Footer ist eine duenne `border-top`
(Spec §cld1-S19 Variante E).

## API-Contract

`FooterInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `segments` | `list[FooterSegment]` | min_length=1 — linke Identitaets-Zeile |
| `links` | `list[FooterLink]` | min_length=1 — rechte Rechtslinks |
| `version` | `str \| None` | Default None — dezente Versions-Anzeige rechts |

`FooterSegment` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `text` | `str` | min_length=1 — Segment-Text |
| `slot_id` | `str \| None` | Default None — wenn gesetzt: client-seitiger Hydration-Slot |

`FooterLink` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `label` | `str` | min_length=1 — Link-Text |
| `href` | `str` | min_length=1 — Ziel-URL |

## Verwendete Tokens

- `color.light.border` — Farbe der "Hochstrich"-Trennlinie
- `color.light.text-muted` — Farbe von Identitaets-Zeile und Links
- `color.light.text-subtle` — Farbe der Version
- `color.light.accent` — `:focus-visible`-Outline der Links
- `stroke.thin` — Staerke der Trennlinie
- `font.body` — Schrift

## Verhalten

- HTML-Struktur: `<footer class="mn-footer">` mit `<div class="mn-footer__inner">`,
  darin `<div class="mn-footer__identity">` (Segmente + `|`-Trenner) und
  `<div class="mn-footer__meta">` (Links + `·`-Trenner + optional Version).
- Segmente werden mit `|` getrennt, der rechte Cluster mit `·`. Die Trenner
  tragen `aria-hidden="true"` (rein dekorativ, fuer Screenreader unsichtbar).
- Ein `FooterSegment` mit `slot_id` rendert als `<span id="…">` — den Inhalt
  fuellt clientseitiges JS (z.B. Profil-Info aus `/api/me`). Ohne `slot_id`
  ist das Segment statischer Text.
- `version` rendert nur, wenn gesetzt — als letztes Element des rechten Clusters.
- `text`, `label`, `href`, `slot_id` und `version` werden per `html.escape()`
  (href/slot_id mit `quote=True`) XSS-sicher ausgegeben.
- `render_footer_css()` liefert die flex-Zeile + die "Hochstrich"-Linie.
- Footer-Links haben einen Token-basierten `:focus-visible`-Indikator (WCAG 2.4.7).

## Varianten

- 1 bis n Identitaets-Segmente, 1 bis n Rechtslinks — die strukturelle Variation.
- Version: vorhanden / fehlend.
- Keine Tier- oder Farbvarianten (Footer ist tier-neutral).

## Plattform-Implementierungen

- `mn_design_system/components/web/footer.py` — HTML- + CSS-Renderer
- PDF/LaTeX — nicht implementiert; ein PDF-Pendant kann spaeter folgen
  (Pattern-First erlaubt das).

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md`;
  die Schlusszeilen-Form (Variante B) wurde cld1-S21 mit KT-1 festgelegt.
- Vorlage: `layout_shared.render_footer` (claudeAI, Welle-1-Stand) — die
  schlanke einzeilige Form, die dieser Footer wiederaufnimmt.
