"""Web-Renderer Stand-Zeile — HTML + CSS + JS, 0.24.0 (Welle 1).

Konsumiert StandZeileInput: „Aktualisiert 14.11. 06:05 · AMBER“, auf jeder Seite. Mit `stand_iso`
und `takt_minuten` traegt die Zeile `data-stand` und `data-takt-min`; `render_stand_zeile_js()`
haengt „· veraltet“ an, wenn der Stand aelter ist als das Doppelte des Takts. Ohne das Skript
erscheint keine Warnung (der Stand der Start-Kacheln heute) — auf statischen Seiten entsteht
„veraltet“ im Browser, nicht im Seitenbau.

Das Skript ist eine EXTERNE Datei (CSP `script-src 'self'`), nimmt nie Markup aus Daten
(`textContent`) und ist idempotent.
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import StandZeileInput


def render_stand_zeile_html(input: StandZeileInput, *, inline_css: bool = False) -> str:
    """Stand-Zeile als `<p class="mn-stand">`; ohne TLP und Takt die schlichte alte Form."""
    attribute = ""
    if input.stand_iso is not None:
        attribute = (
            f' data-stand="{escape(input.stand_iso, quote=True)}"'
            f' data-takt-min="{input.takt_minuten}"'
        )
    tlp = (
        f' · <span class="mn-stand__tlp">{escape(input.tlp)}</span>'
        if input.tlp is not None
        else ""
    )
    html = f'<p class="mn-stand"{attribute}>{escape(input.text)}{tlp}</p>'
    if inline_css:
        return f"<style>{render_stand_zeile_css()}</style>{html}"
    return html


def render_stand_zeile_css() -> str:
    """Komponenten-CSS — Feinzeile in `web.text.caption`, „veraltet“ in der Warnfarbe."""
    return """
.mn-stand {
  margin: 0;
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-stand__tlp {
  font-weight: 600;
}
.mn-stand__veraltet {
  font-weight: 600;
  color: var(--color-status-urgent, #e65100);
}
""".strip()


_JS = """
(function () {
  function pruefe() {
    Array.prototype.forEach.call(
      document.querySelectorAll(".mn-stand[data-stand][data-takt-min]"),
      function (zeile) {
        if (zeile.querySelector(".mn-stand__veraltet")) return;
        var stand = Date.parse(zeile.getAttribute("data-stand"));
        var takt = Number(zeile.getAttribute("data-takt-min"));
        if (!isFinite(stand) || !(takt > 0)) return;
        if (Date.now() - stand <= 2 * takt * 60000) return;
        var marke = document.createElement("span");
        marke.className = "mn-stand__veraltet";
        marke.textContent = " · veraltet";
        zeile.appendChild(marke);
      }
    );
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", pruefe);
  } else {
    pruefe();
  }
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) pruefe();
  });
})();
"""


def render_stand_zeile_js() -> str:
    """Skript, das „· veraltet“ anhaengt, wenn der Stand aelter ist als das Doppelte des Takts.

    Einbindung wie `render_sub_nav_js()`: als eigene Datei ablegen und per
    `<script src="…" defer></script>` einbinden (nie Inline; unter einer Nonce-CSP traegt das Tag
    das nonce). Liest `data-stand` (ISO-8601 mit Zone) und `data-takt-min`; ein unlesbarer Stand
    aendert nichts, ein Stand in der Zukunft ist nie veraltet. Nach einem Tab-Wechsel zurueck
    wird neu geprueft (eine lange offene Seite altert).
    """
    return _JS.strip() + "\n"
