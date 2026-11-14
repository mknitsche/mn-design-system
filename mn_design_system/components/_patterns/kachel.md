# Kachel, Status-Punkt, Fortschritt

> Bausteine fuer Uebersichtsseiten (Foyer): die Kachel mit Raster, der Status-Punkt (Symbol + Wort) und der Fortschritt. Seit 0.24.0.

## API-Contract

- `KachelInput(kicker, titel_id, display_zahl=None, inhalt_html="", fuss_link=None, stand=None)`; `render_kachel_html` erzeugt
  `<section class="mn-kachel" aria-labelledby=titel_id>` mit `<h3>` (Kicker), Zahl, Inhalt, Stand und Fusslink. `fuss_link` ist `(href, label)`,
  `href` intern oder relativ. `titel_id` muss eine gueltige HTML-id sein.
  **`inhalt_html` wird nicht escapt** (Markup aus anderen DS-Renderern): der Konsument setzt jeden Text darin mit `html.escape(text, quote=True)` ein;
  Werte aus Owner-Daten gehoeren nie dorthin, sondern kommen im Browser per `textContent` (Regel P11).
- `render_kachel_css()` enthaelt das Raster `mn-kachel-raster`: eine Spalte, ab `web.layout.bp-tablet` zwei (das feste `900px` der Startseite entfaellt).
- `StatusPunktInput(stufe: ok|warn|alarm|unbekannt, wort)`: Symbol (✓ ▲ ✕ –, `aria-hidden`) und Wort, nie Farbe allein.
- `FortschrittInput(anteil 0..1, label)`: `role="progressbar"` mit `aria-valuenow`; die Fuellung ist ein SVG-Rechteck, kein `style`-Attribut (CSP).

## Verwendete Tokens

`web.text.*`, `web.leading.*`, `web.touch-target`, `web.stroke.*`, `web.color.*`, `color.light.*`, `color.status.success|warning|urgent|error` und
`-bg`, `radius.subtle|round`, `space.1`–`space.4`, `web.layout.bp-tablet`.
