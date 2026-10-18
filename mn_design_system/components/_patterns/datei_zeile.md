# Listenzeile (Ordner/Datei)

> Eine Zeile einer ruhigen Datei-Liste: Kennung oder Vorschau, Name, Meta, Aktion. Tier-neutral.

## Anatomie

```
[PDF]  plan.pdf                      heute 06:40   1,2 MB   ⋯     <- Dateizeile
[   ]  Berichte                      12.10.        3 Dateien ›     <- Ordnerzeile (ganze Zeile ist der Link)
```

`<ul class="mn-datei-liste">` mit je `<li class="mn-datei-zeile">` (Ordner: `--ordner`). Bis
`web.layout.bp-mobile` zweizeilig (Name / Meta), die Groesse entfaellt am Telefon.

## API-Contract

`DateiZeileInput` (Pydantic, frozen, `extra="forbid"`, siehe `contracts.py`): `name`, `href`, `art`
(`ordner`|`datei`), optional `kennung`, `vorschau_src` (ersetzt die Kennung), `datum`, `groesse`
(Datei) bzw. `inhalt` (Ordner), `satz`, `etikett`, `neu`, `aktion_label` (Datei: Knopf `⋯`).
`href` und `vorschau_src`: interner oder relativer Pfad, kein Schema, kein `//`, kein Backslash.

`render_datei_zeile_html(z, *, inline_css=False)`, `render_datei_liste_html(zeilen, *, label, inline_css=False)`,
`render_datei_zeile_css()`.

## Klassenvertrag

`mn-datei-liste`, `mn-datei-zeile` (+ `--ordner`), `__kennung`, `__vorschau`, `__name`, `__satz`,
`__etikett`, `__meta` (+ `--groesse`), `__neu`, `__aktion`. Ein Browser-Konsument baut dieselben Klassen per DOM.

## Regel (Verwendung)

- Ordner zuerst, dann Dateien, keine Zwischenueberschriften — die Reihenfolge ist Sache des Konsumenten.
- Schriftgrade genau drei: Name 16 (`web.text.body`), Meta 14 (`web.text.ui`), Kennung/Etikett/neu 12 (`web.text.caption`).

## Verwendete Tokens

`web.text.*`, `web.leading.*`, `web.touch-target`, `web.stroke.line/focus`, `web.layout.bp-mobile`,
`web.color.focus-ring`, `color.light.*`, `space.*`, `radius.subtle`, `font.weight.medium`, `font.tracking.wide`.
Keine Literalfarbe und keine feste Laenge ausser als `var()`-Rueckfall.
