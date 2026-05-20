# Footer

> Seiten-Fuss von mkn-desk.com: bis zu drei Link-Spalten plus eine optionale Meta-Zeile (Version + Copyright-Notiz). Tier-neutral — auf jeder Seite identisch.

## Anatomie

```
─────────────────────────────────────────────────────────────  <- Hochstrich (border-top)
  BEREICHE        RECHTLICHES       KONTAKT
  Start           Impressum         E-Mail
  Bibliothek      Datenschutz

  © 2026 MN                                            v0.2.0   <- Meta (optional)
```

`<footer>` mit einem Grid aus bis zu 3 Spalten (`<h2>`-Spaltentitel +
`<ul>`-Linkliste). Darunter optional eine Meta-Zeile mit Copyright-Notiz
links und Version rechts. Die "Hochstrich"-Trennlinie ueber dem Footer ist
eine duenne `border-top` (Spec §cld1-S19 Variante E).

## API-Contract

`FooterInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `columns` | `list[FooterColumn]` | min_length=1, max_length=3 |
| `version` | `str \| None` | Default None — Versions-Anzeige (z.B. "v0.2.0") |
| `note` | `str \| None` | Default None — Copyright-/Hinweis-Text |

`FooterColumn` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `title` | `str` | min_length=1, Spaltentitel |
| `links` | `list[FooterLink]` | min_length=1 |

`FooterLink` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `label` | `str` | min_length=1, Link-Text |
| `href` | `str` | min_length=1, Ziel-URL |

## Verwendete Tokens

- `color.light.border` — Farbe der "Hochstrich"-Trennlinie
- `color.light.text` — Farbe der Links
- `color.light.text-muted` — Farbe der Spaltentitel
- `color.light.text-subtle` — Farbe der Meta-Zeile
- `stroke.thin` — Staerke der Trennlinie
- `font.body` — Schrift

## Verhalten

- HTML-Struktur: `<footer class="mn-footer">` mit
  `<div class="mn-footer__columns">` (pro Spalte `<div class="mn-footer__col">`
  mit `<h2 class="mn-footer__col-title">` + `<ul>`/`<li>`/`<a>`) und — falls
  `version` oder `note` gesetzt — `<div class="mn-footer__meta">`.
- Die Meta-Zeile wird nur gerendert, wenn `version` ODER `note` gesetzt ist.
  Innerhalb der Meta-Zeile steht `note` links, `version` rechts; jedes Element
  erscheint nur, wenn es gesetzt ist.
- `label`, `href`, `title`, `version` und `note` werden per `html.escape()`
  (href mit `quote=True`) XSS-sicher ausgegeben.
- `render_footer_css()` liefert das 3-Spalten-Grid + die "Hochstrich"-Linie.

## Varianten

- 1 bis 3 Spalten — die strukturelle Variation.
- Meta-Zeile: keine / nur Version / nur Note / beides. Keine Tier- oder
  Farbvarianten (Footer ist tier-neutral).

## Plattform-Implementierungen

- `mn_design_system/components/web/footer.py` — HTML + CSS-Renderer
- PDF/LaTeX — nicht in Welle A; ein PDF-Pendant kann spaeter folgen
  (Pattern-First erlaubt das).

## Referenzen

- Spec: `claudeAI docs/superpowers/specs/2026-05-19-ux-aufwertung-v02-design.md` §Welle A (Footer — Contract `FooterInput` 3-Block + Version) + §cld1-S19 Variante E (Hochstrich-Trennlinie)
