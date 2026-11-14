# Profil-Menue und Schema-Skript

> Profil-Knopf im Kopf, das Menue „Darstellung“ und das Skript, das die Wahl vor dem ersten Zeichnen setzt. Seit 0.24.0.

## API-Contract

- `ProfilMenueInput(profil_href, titel="Darstellung")`; `profil_href` nur ein interner absoluter Pfad (kein Schema, kein `//`, kein Backslash, keine Leer- oder Steuerzeichen).
- `MastheadInput.profil: ProfilMenueInput | None = None`. Gesetzt: im Kontext-Slot steht der Knopf `<button class="mn-masthead__profil" type="button" popovertarget="profilmenue"
  aria-label="Profil und Darstellung">` (am Rechner und am Handy) samt Rueckfall-Link `a.mn-masthead__profil-link` auf `#profilmenue`; das CSS zeigt genau einen.
  In der kompakten Form sind die Chips am Handy verborgen, am Rechner bleibt der Chip unveraendert.
- `render_profilmenue_html(ProfilMenueInput)` erzeugt `<div id="profilmenue" class="mn-profilmenue" popover>` mit drei Knoepfen `data-schema-wahl="auto|hell|dunkel"` (`aria-pressed`)
  und dem Link „Profil ansehen“. Der Konsument setzt es ans Seitenende (wie den Raumplan). `render_profilmenue_css()` traegt auch die Regeln des Knopfes im Kopf.
- `render_schema_js() -> str`, parameterlos, eine externe Datei, synchron im `<head>` vor dem Stylesheet. Die Wahl (`localStorage`, Schluessel `mn-schema`: `auto|hell|dunkel`)
  liegt nur im Browser. `data-schema` auf `<html>`: `dunkel` bei dunkler Seite (Wahl dunkel, oder auto bei dunkler Systemeinstellung — so liest es der Diagramm-Loader),
  `hell` bei ausdruecklicher Wahl hell, sonst entfaellt das Attribut. Eine Aenderung laedt die Seite neu, wenn Diagramme (`[data-verlauf-chart]`) auf ihr stehen.

## Rueckfall

Nur unter `@supports selector(:popover-open)` ist das Menue schwebend und der Knopf ein Knopf; sonst steht das Menue als sichtbarer Abschnitt am Seitenende und der Knopf ist ein Link. Das Menue ist nie unerreichbar.

## Verwendete Tokens

`web.text.*`, `web.leading.ui`, `web.touch-target`, `web.stroke.*`, `web.color.*`, `color.light.*`, `color.dark.text`, `radius.card|round`, `space.1`–`space.4`, `web.layout.page-inset`, `web.layout.bp-mobile`.
