# Ortszeile

> Die ganze Kette vom Raum bis zur Elternseite als eine Zeile: `Observatorium › Gesundheit › ← Schlaf`. Tier-neutral. Seit 0.24.0.

## API-Contract

`OrtszeileInput(glieder=((href, label), ...))` (Pydantic, frozen, `extra="forbid"`), mindestens ein Glied; `href`: interner
oder relativer Pfad, kein Schema; `label` nicht leer. Das **letzte** Glied ist die Elternseite.
`render_ortszeile_html(o, *, inline_css=False)` liefert `<nav class="mn-ortszeile" aria-label="Ort"><ol>` mit `<li><a>` je
Glied; das letzte `<a class="mn-ortszeile__eltern">` beginnt mit „← “. `render_ortszeile_css()`.

## Regel (Verwendung)

Welche Kette gezeigt wird, entscheidet der Konsument. `back_link` und `pfad_zeile` bleiben unveraendert und werden von der
Ortszeile nicht ersetzt. Die Zeile ist einzeilig: am schmalen Bildschirm kuerzen die vorderen Glieder mit „…“, das letzte
Glied schrumpft nie. Zielhoehe der Links: `web.touch-target`.

## Verwendete Tokens

`web.text.ui`, `web.leading.ui`, `color.light.text-muted`, `color.light.accent` (Hover), `web.touch-target`,
`web.stroke.focus`, `web.color.focus-ring`, `space.1`, `space.2`.
