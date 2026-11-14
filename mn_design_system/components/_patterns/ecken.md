# Eckenregel

> Eine CSS-Funktion ueber die vorhandenen Radius-Tokens (Spec 4.6, Welle 1). Seit 0.24.0, additiv.

## API-Contract

- `render_ecken_css() -> str`, parameterlos. Einbinden NACH dem Komponenten-CSS. Der Konsument setzt keinen Radius selbst.
- Rollen-Variablen auf `:root`: `--mn-r-flaeche` (= `radius-card`), `--mn-r-innen` (= `max(0px, calc(var(--mn-r-flaeche) - var(--space-4)))`),
  `--mn-r-bedien` (= `radius-round`), `--mn-r-leiste` (= `radius-none`).
- **Flaechen** (`mn-kachel`, `mn-content-card`, `mn-kpi-card`, `mn-profilmenue`, `mn-aufklapper`, `mn-empty-state`, das Blatt des Raumplans nur oben): `--mn-r-flaeche`.
- **Innen** (`mn-innen`, `mn-datei-zeile__vorschau`, Code in Chat-Nachrichten): innen = aussen − Innenabstand (`space.4`), nie weniger als 0; in CSS gerechnet, nicht gesetzt.
- **Anklickbares und Etiketten** (Pillen, Chips, Profil-Knopf, Raum-Umschalter, Schalter, Etiketten, Status-Punkt, Zeitraum-Optionen, Fokusrahmen im Raumplan und Profil-Menue): `--mn-r-bedien`.
- **Leisten an der Kante** (Masthead und seine Baender, Unterleiste, Fusszeile): `--mn-r-leiste`.
- `mn-aufklapper` ist die Klasse fuer die Flaeche eines Aufklappers (`<details>`); die Komponente dazu gibt es nicht, nur die Rolle.

## Verwendete Tokens

`radius.card`, `radius.round`, `radius.none`, `space.4`.
