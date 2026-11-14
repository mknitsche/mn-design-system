# Kachel, Status-Punkt, Fortschritt

> Bausteine fuer Uebersichtsseiten (Foyer): die Kachel mit Raster, der Status-Punkt (Symbol + Wort) und der Fortschritt. Seit 0.24.0.

## API-Contract

- `KachelInput(kicker, aussage, link, titel_id, zahl=None, stand=None, status=None)` (streng, seit 0.24.0): `render_kachel_html` erzeugt
  `<section class="mn-kachel" aria-labelledby=titel_id>` mit `<h3>` (Kicker), optional Status-Punkt und Zahl, EINER Aussage, optional Stand und genau einem
  `<a class="mn-kachel__link">`. `link` ist `(label, href)`, `href` nur ein interner absoluter Pfad. Es gibt **kein freies HTML** (`inhalt_html` entfaellt):
  jedes Feld wird escapt, keine Liste, keine Tabelle. Die ganze Kachel ist ueber den einen Link klickbar (Pseudo-Element `::after`, kein zweiter Link im DOM).
  Ohne `zahl` zeigt die Kachel keine. `titel_id` muss eine gueltige HTML-id sein.
- `render_kachel_css()` enthaelt das Raster `mn-kachel-raster`: eine Spalte, ab `web.layout.bp-tablet` zwei (das feste `900px` der Startseite entfaellt).
- `StatusPunktInput(stufe: ok|warn|alarm|unbekannt, wort)`: Symbol (✓ ▲ ✕ –, `aria-hidden`) und Wort, nie Farbe allein.
- `FortschrittInput(anteil 0..1, label, label_id)`: `role="progressbar"` mit `aria-valuenow`, Name per `aria-labelledby` auf den sichtbaren Label-Span (`label_id`, eindeutig je Seite); die Fuellung ist ein SVG-Rechteck, kein `style`-Attribut (CSP).

## Verwendete Tokens

`web.text.*`, `web.leading.*`, `web.touch-target`, `web.stroke.*`, `web.color.*`, `color.light.*`, `color.status.success|warning|urgent|error` und
`-bg`, `radius.card|subtle|round`, `space.1`–`space.4`, `web.layout.bp-tablet`.
