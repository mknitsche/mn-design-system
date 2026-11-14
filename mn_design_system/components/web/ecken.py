"""Eckenregel — CSS, 0.24.0 (Welle 1, Plan T24; Spec 4.6).

`render_ecken_css()` ist EINE CSS-Funktion ueber die vorhandenen Radius-Tokens; der Konsument setzt
nie einen Radius selbst. Sie wird NACH dem Komponenten-CSS eingebunden und gibt jeder Klasse eine
Rolle:

- **Flaeche** (`--mn-r-flaeche` = `radius-card`): Kachel, Karte, Profil-Menue, Aufklapper, Blatt.
- **Innen** (`--mn-r-innen`): was in einer Flaeche liegt, bekommt innen = aussen − Innenabstand
  (`space.4`), nie weniger als 0; der Wert wird in CSS gerechnet, nicht gesetzt. Klasse `mn-innen`.
- **Bedienelement und Etikett** (`--mn-r-bedien` = `radius-round`): Pillen, Chips, Profil-Knopf,
  Raum-Umschalter, Schalter, Etiketten, Status-Punkt und der Fokusrahmen dieser Elemente.
- **Leiste an der Kante** (`--mn-r-leiste` = `radius-none`): Kopfband, Unterleiste, Fusszeile.

Additiv: ohne diesen Aufruf aendert sich kein bestehendes CSS.
"""

from __future__ import annotations

_FLAECHE = (
    ".mn-kachel",
    ".mn-content-card",
    ".mn-kpi-card",
    ".mn-profilmenue",
    ".mn-aufklapper",
    ".mn-empty-state",
)
_BEDIEN = (
    ".mn-masthead__pill",
    ".mn-masthead__chip",
    ".mn-masthead__profil",
    ".mn-masthead__profil-link",
    ".mn-masthead__raum",
    ".mn-masthead__raum-link",
    ".mn-profilmenue__wahl",
    ".mn-raumplan__schliessen",
    ".mn-tier-chip",
    ".mn-status",
    ".mn-stand__tlp",
    ".mn-sub-nav__feld",
    ".mn-zeitraum-leiste",
    ".mn-zeitraum-leiste__option",
    ".mn-chat-composer__btn",
    ".mn-chat-tool-badge",
)
_LEISTE = (
    ".mn-masthead",
    ".mn-masthead__identity",
    ".mn-masthead__tiers",
    ".mn-sub-nav",
    ".mn-sub-nav__inner",
    ".mn-footer",
)
_INNEN = (
    ".mn-innen",
    ".mn-datei-zeile__vorschau",
    ".mn-chat-message__body code",
    ".mn-chat-message__body pre",
)


def _regel(klassen: tuple[str, ...], rolle: str) -> str:
    return ",\n".join(klassen) + f" {{\n  border-radius: var(--mn-r-{rolle});\n}}"


def render_ecken_css() -> str:
    """Rollen-Variablen auf `:root` und die Regeln aller Klassen der Rollen."""
    return "\n".join(
        [
            """
:root {
  --mn-r-flaeche: var(--radius-card, 4px);
  --mn-r-innen: max(0px, calc(var(--mn-r-flaeche) - var(--space-4, 16px)));
  --mn-r-bedien: var(--radius-round, 9999px);
  --mn-r-leiste: var(--radius-none, 0);
}""".strip(),
            _regel(_FLAECHE, "flaeche"),
            _regel(_INNEN, "innen"),
            _regel(_BEDIEN, "bedien"),
            _regel(_LEISTE, "leiste"),
            # Fokusrahmen: der Rahmen folgt dem Radius seines Elements — Links in Flaechen sind rund
            (
                ".mn-raumplan a:focus-visible,\n"
                ".mn-profilmenue a:focus-visible {\n"
                "  border-radius: var(--mn-r-bedien);\n}"
            ),
            # das Blatt des Raumplans sitzt unten an der Kante: nur die oberen Ecken sind Flaeche
            (
                "@supports selector(:popover-open) {\n"
                "  .mn-raumplan {\n"
                "    border-radius: var(--mn-r-flaeche) var(--mn-r-flaeche) 0 0;\n"
                "  }\n}"
            ),
        ]
    )
