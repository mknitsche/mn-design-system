"""Schema-Skript (Hell / Dunkel / Automatisch) — JS, 0.24.0 (Welle 1, Plan T24).

`render_schema_js()` ist parameterlos und liefert EINE externe Skriptdatei (CSP `script-src 'self'`,
nie Inline). Sie steht synchron im `<head>`, VOR dem Stylesheet und dem Diagramm-Loader, damit beim
ersten Zeichnen nichts aufblitzt. Sie loest `mn-schema.js` der Connector-Seiten ab.

Die Wahl liegt nur im Browser (`localStorage`, Schluessel `mn-schema`: `auto`, `hell` oder
`dunkel`; ohne oder mit ungueltigem Wert gilt `auto`). Das Skript setzt `data-schema` auf `<html>`:
`dunkel`, wenn die Seite dunkel ist (Wahl dunkel, oder Wahl auto bei dunkler Systemeinstellung —
so liest es der Diagramm-Loader), `hell` bei ausdruecklicher Wahl hell, sonst entfaellt das
Attribut. Es bedient die Knoepfe `[data-schema-wahl]` des Profil-Menues (`aria-pressed`). Eine
Aenderung der Darstellung laedt die Seite neu, wenn Diagramme auf ihr stehen (sie zeichnen ihre
Farben einmal beim Laden); sonst nicht.
"""

from __future__ import annotations

_JS = """
(function () {
  var KEY = "mn-schema";
  var root = document.documentElement;
  var mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  function wahl() {
    var w = "auto";
    try { w = window.localStorage.getItem(KEY) || "auto"; } catch (e) {}
    return w === "hell" || w === "dunkel" ? w : "auto";
  }
  function wirkung(w) {
    if (w === "dunkel") return "dunkel";
    if (w === "hell") return "hell";
    return mq && mq.matches ? "dunkel" : "";
  }
  function anwenden() {
    var w = wahl();
    var s = wirkung(w);
    if (s) root.setAttribute("data-schema", s);
    else root.removeAttribute("data-schema");
    Array.prototype.forEach.call(
      document.querySelectorAll("[data-schema-wahl]"),
      function (knopf) {
        knopf.setAttribute(
          "aria-pressed",
          String(knopf.getAttribute("data-schema-wahl") === w)
        );
      }
    );
  }
  function hatDiagramme() {
    return !!document.querySelector("[data-verlauf-chart]");
  }
  anwenden();
  if (mq && mq.addEventListener) {
    mq.addEventListener("change", function () {
      if (wahl() !== "auto") return;
      anwenden();
      if (hatDiagramme()) window.location.reload();
    });
  }
  document.addEventListener("click", function (ereignis) {
    var ziel = ereignis.target;
    var knopf = ziel && ziel.closest ? ziel.closest("[data-schema-wahl]") : null;
    if (!knopf) return;
    var neu = knopf.getAttribute("data-schema-wahl");
    if (neu !== "auto" && neu !== "hell" && neu !== "dunkel") return;
    var vorher = wirkung(wahl());
    try { window.localStorage.setItem(KEY, neu); } catch (e) {}
    anwenden();
    if (wirkung(neu) !== vorher && hatDiagramme()) window.location.reload();
  });
  document.addEventListener("DOMContentLoaded", anwenden);
})();
"""


def render_schema_js() -> str:
    """Skript, das `data-schema` vor dem ersten Zeichnen setzt und die drei Knoepfe bedient.

    Einbindung wie `render_sub_nav_js()`: als eigene Datei ablegen und synchron im `<head>` per
    `<script src="…"></script>` einbinden (ohne `defer`, damit es vor dem ersten Zeichnen laeuft).
    """
    return _JS.strip() + "\n"
