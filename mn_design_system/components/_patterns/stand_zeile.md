# Stand-Zeile

> „Aktualisiert 14.11. 06:05 · AMBER“ auf jeder Seite; ab dem Doppelten des Takts „· veraltet“. Seit 0.24.0.

## API-Contract

`StandZeileInput(text, tlp=None, stand_iso=None, takt_minuten=None)`: `text` ist der fertige Stand-Text, `tlp` das Etikett dahinter. `stand_iso`
(ISO-8601 **mit Zone**) und `takt_minuten` (> 0) gibt es nur zusammen. `render_stand_zeile_html` erzeugt `<p class="mn-stand">`; ohne TLP, Stand und Takt
ist das die schlichte alte Form `<p class="mn-stand">text</p>`, sonst mit `data-stand` und `data-takt-min`. `render_stand_zeile_css()`.

`render_stand_zeile_js()` liefert das Skript, das `· veraltet` (`span.mn-stand__veraltet`) anhaengt, wenn `jetzt − stand > 2 × takt`. Eigene Datei,
`<script src defer>`, nie Inline (CSP); `textContent` statt Markup; idempotent; ein unlesbarer oder zukuenftiger Stand aendert nichts; neue Pruefung nach
`visibilitychange`. Ohne das Skript erscheint keine Warnung — „veraltet“ entsteht im Browser, nicht im Seitenbau (P9). Takt je Familie: stuendlich
(Seitenbau), 30 Minuten (Heute), je Aufruf (Connector) — das entscheidet der Konsument.

## Verwendete Tokens

`web.text.caption`, `web.leading.caption`, `web.font.sans`, `color.light.text-muted`, `color.status.urgent`.
