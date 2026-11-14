# Raumplan und kompakter Kopf

> Die Handy-Form der Raumleiste: ein Blatt mit allen Raeumen, Zwecksatz und Reitern. Der kompakte Kopf (`masthead`) oeffnet es. Seit 0.24.0, streng additiv.

## API-Contract

`RaumplanRaum(slug, label, href, zweck, reiter, gruppen=None)` — `reiter` und die Reiter der `gruppen` sind `(label, href)`-Paare,
`gruppen` eine Liste `(gruppenname, [(label, href), ...])`; `href` intern oder relativ, kein Schema. `RaumplanInput(raeume, titel="Alle Räume")`.
`render_raumplan_html(r, *, inline_css=False)` erzeugt `<section id="raumplan" class="mn-raumplan" popover aria-labelledby="raumplan-titel">`
mit je einem `<li data-bereich="<slug>">` (Raum-Link, Zwecksatz, Reiter, Gruppen) und einem Schliessen-Knopf. `render_raumplan_css()`.

`MastheadInput` bekommt `form: Literal["klassisch", "kompakt"] = "klassisch"`, `blicke: int = 0` und `raum_schalter: str | None = None`
(die zwei letzten nur mit `form="kompakt"`). `render_masthead_css(kompakt=True)` haengt die Regeln der kompakten Form an; ohne neue
Argumente sind HTML und CSS byte-gleich zu 0.23.0 (Golden-Test).

## Regel (Verwendung)

- **Rechner und iPad:** wie bisher zwei Reihen; neu steht ein Trenner zwischen den ersten `blicke` Pillen (Start, Heute) und den Raeumen.
- **Handy (bis `web.layout.bp-mobile`):** EINE Zeile `[Marke] Start · Heute · [Raum ▾] … [Profil]`. Markenzeile (Wortmarke, Datum) und
  Raum-Pillen (`mn-masthead__pill--raum`) sind verborgen. Die Zeile ist 44 px hoch (`web.touch-target`); Kopf + Unterleiste belegen bei 390 px
  weniger als 100 px, mit Gruppen-Schalter weniger als 140 px (im Browser belegt).
- **Raum-Schalter** steht doppelt im HTML: `<button popovertarget="raumplan">` und `<a href="#raumplan">`; `@supports selector(:popover-open)` zeigt den
  Knopf, sonst den Link. Der Konsument setzt `raum_schalter` auf den Namen des aktiven Raums (auf Start und Heute „Räume“).
- **Rueckfall:** das Blatt (feste Lage unten, Hintergrund-Abdunklung) gibt es nur unter `@supports selector(:popover-open)`; sonst bleibt der
  Raumplan ein sichtbarer Abschnitt „Alle Räume“ (`display: block` auch gegen eine UA-Regel fuer `[popover]`). Kein Raum wird unerreichbar.
- Der Konsument setzt den Raumplan als letzten Block vor die Fusszeile und befuellt ihn nur mit Zielen der Ebenen 1 und 2; welche Raeume ein Gast sieht,
  entscheidet er.

## Verwendete Tokens

`web.text.ui`, `web.text.caption`, `web.text.h3`, `web.leading.ui`, `web.touch-target`, `web.stroke.line`, `web.stroke.line-strong`,
`web.stroke.focus`, `web.color.separator`, `web.color.separator-on-dark` (Trenner), `web.color.focus-ring`, `color.light.*`, `color.dark.*`,
`radius.subtle`, `radius.round`, `space.1`–`space.4`, `web.layout.page-inset`, `web.layout.bp-mobile`.
