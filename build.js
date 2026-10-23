/**
 * MN PKA Design-System — Build Script
 *
 * Liest Tokens aus tokens/*.json (alle automatisch), generiert:
 *   dist/css/tokens.css      — CSS Custom Properties (Web)
 *   dist/python/tokens.py    — Python-Dict (claudeAI ReportLab)
 *   dist/json/tokens.json    — flach, fuer beliebige Konsumenten
 *   mn_design_system/latex/mn-design.sty — LaTeX-Paket (Farben, \mnToken, Schriften)
 *
 * Aufruf: npm run build
 */

import StyleDictionary from "style-dictionary";
import fs from "node:fs";

// ---------------------------------------------------------------------------
// Custom Format: Python
// ---------------------------------------------------------------------------
StyleDictionary.registerFormat({
  name: "python/dict",
  format: ({ dictionary, file }) => {
    const lines = [
      `"""${file?.comment || "MN PKA Design-System Tokens — auto-generiert."}"""`,
      "",
      "# Auto-generiert aus tokens/*.json via Style Dictionary.",
      "# NICHT MANUELL BEARBEITEN — Aenderungen werden ueberschrieben.",
      "",
      "TOKENS = {",
    ];
    for (const tok of dictionary.allTokens) {
      const key = tok.path.join(".");
      let val = tok.value;
      if (typeof val === "string") {
        val = `"${val.replace(/"/g, '\\"')}"`;
      } else if (typeof val === "boolean") {
        val = val ? "True" : "False";
      } else {
        val = String(val);
      }
      lines.push(`    "${key}": ${val},`);
    }
    lines.push("}");
    lines.push("");
    lines.push("# Helper");
    lines.push("def get(key, default=None):");
    lines.push('    """Token-Lookup mit Default. Beispiel: get("color.light.text")."""');
    lines.push("    return TOKENS.get(key, default)");
    lines.push("");
    return lines.join("\n");
  },
});

// ---------------------------------------------------------------------------
// Custom Format: JSON dotted (color.light.text statt ColorLightText)
// ---------------------------------------------------------------------------
StyleDictionary.registerFormat({
  name: "json/dotted",
  format: ({ dictionary }) => {
    const out = {};
    for (const tok of dictionary.allTokens) {
      out[tok.path.join(".")] = tok.value;
    }
    return JSON.stringify(out, null, 2);
  },
});

// ---------------------------------------------------------------------------
// LaTeX-Schicht: EIN Paket mn-design.sty (v0.21.0)
// ---------------------------------------------------------------------------
// Die einzige LaTeX-Ausgabe des Design-Systems (bis 0.20.0 gab es dist/latex/tokens.tex mit
// "#" im \def — das TeX-Parameterzeichen — und Makronamen mit Ziffern, beides unbenutzbar, und
// ausserhalb des Wheels). Das Paket enthaelt:
//   * jede Farbe als xcolor-Farbe "mn-<pfad>" (z. B. mn-color-light-h1) + die semantischen
//     Dokumentfarben (claudeAI design-standards.md § 1),
//   * alle Druck-Tokens (font.*, space.*, stroke.*) ueber EINEN Zugriff \mnToken{<pfad>} —
//     ein unbekannter Pfad bricht laut ab,
//   * die Schriften per Pfad aus dem Paket, nie ueber Fontconfig (seit 0.20.0 liegen unter
//     fonts/web/ .woff2-Dateien, die XeTeX ueber Fontconfig waehlt und nicht einbetten kann):
//     Geist (Kursiv = Source Serif 4 Italic), JetBrains Mono, STIX Two Math (unicode-math),
//     Noto Sans Symbols 2 fuer Haken/Kreuz.
const LATEX_SEMANTIK = [
  ["mnText", "color.light.text"],
  ["mnHOne", "color.light.h1"],
  ["mnHTwo", "color.light.h2"],
  ["mnAccent", "color.light.accent"],
  ["mnAccentSoft", "color.light.accent-soft"],
  ["mnSurfaceSubtle", "color.light.surface-subtle"],
  ["mnGreySeven", "color.grey.700"],
  ["mnGreyFive", "color.grey.500"],
  ["mnGreyThree", "color.grey.300"],
  ["mnBrand", "color.brand"],
  ["mnStatusSuccess", "color.status.success"],
  ["mnStatusWarning", "color.status.warning"],
  ["mnStatusError", "color.status.error"],
];
// Druck-Tokens, die \mnToken anbietet (web.*, shadow.*, radius.* sind CSS-Begriffe).
const LATEX_TOKEN_GRUPPEN = ["font", "space", "stroke"];
// Zeichen, die Geist nicht fuehrt und Noto Sans Symbols 2 liefert.
const LATEX_SYMBOLE = ["✓", "✔", "✗", "✘"];
// Griechisch im Fliesstext: Geist fuehrt es nicht, xelatex liesse die Zeichen nur mit einer Warnung
// fallen. Ausweichschrift laut Token font.family.fallback-greek (STIX Two Math).
const LATEX_GRIECHISCH = [
  ...Array.from({ length: 0x03a9 - 0x0391 + 1 }, (_, i) => 0x0391 + i).filter((c) => c !== 0x03a2),
  ...Array.from({ length: 0x03c9 - 0x03b1 + 1 }, (_, i) => 0x03b1 + i),
].map((c) => String.fromCodePoint(c));

// Paket-Kennung fuer \ProvidesPackage: LaTeX erwartet "JJJJ/MM/TT vX.Y.Z" (ohne Datum bricht das
// Einbinden mit "Missing = inserted for \ifnum"). Datum aus dem CHANGELOG-Eintrag der Version —
// reproduzierbar (CI vergleicht die Ausgaben) und ohne zweite Pflegestelle.
function latexPaketKennung() {
  const version = JSON.parse(fs.readFileSync("package.json", "utf8")).version;
  const m = new RegExp(`^## \\[${version.replace(/\./g, "\\.")}\\] — (\\d{4})-(\\d{2})-(\\d{2})`, "m").exec(
    fs.readFileSync("CHANGELOG.md", "utf8"),
  );
  if (!m) throw new Error(`latex/sty: CHANGELOG.md hat keinen Eintrag "## [${version}] — JJJJ-MM-TT"`);
  return `${m[1]}/${m[2]}/${m[3]} v${version} MN PKA Design-System`;
}

// Token-Werte als TeX-Text: die Sonderzeichen werden maskiert, sonst bricht \def.
function texText(wert) {
  return String(wert).replace(/[\\#%&_{}$^~]/g, (z) => ({ "\\": "\\textbackslash{}", "^": "\\textasciicircum{}", "~": "\\textasciitilde{}" })[z] || `\\${z}`);
}

StyleDictionary.registerFormat({
  name: "latex/sty",
  format: ({ dictionary }) => {
    const farbname = (pfad) => "mn-" + pfad.join("-");
    const lines = [
      "% mn-design.sty — MN PKA Design-System fuer Pandoc/XeLaTeX. Die EINZIGE LaTeX-Schicht.",
      "% Auto-generiert aus tokens/*.json via Style Dictionary (build.js, Format latex/sty).",
      "% NICHT MANUELL BEARBEITEN — Aenderungen werden ueberschrieben.",
      "%",
      "% Nutzung (Python: mn_design_system.latex.LATEX_DIR / mn_design_system.fonts.FONT_DIR):",
      "%   TEXINPUTS=<LATEX_DIR>//:   und vor \\usepackage{mn-design}:  \\def\\mndsfontdir{<FONT_DIR>}",
      "% Bietet: Farben mn-<pfad> (z. B. mn-color-light-h1) und mnText, mnHOne, mnHTwo, mnAccent,",
      "%   mnAccentSoft, mnSurfaceSubtle, mnGreySeven, mnGreyFive, mnGreyThree, mnBrand, mnStatus*;",
      "%   \\mnToken{<pfad>} fuer font.*, space.*, stroke.* (z. B. \\mnToken{font.size.body});",
      "%   Schriften Geist / Source Serif 4 Italic / JetBrains Mono / STIX Two Math / Noto Sans Symbols 2.",
      "\\NeedsTeXFormat{LaTeX2e}",
      `\\ProvidesPackage{mn-design}[${latexPaketKennung()}]`,
      "\\RequirePackage[table]{xcolor}",
      "\\RequirePackage{fontspec}",
      "\\RequirePackage{unicode-math}",
      "\\RequirePackage{newunicodechar}",
      "",
      "% --- Farben: jedes color.*-Token -------------------------------------------",
    ];
    const definiert = new Set();
    for (const tok of dictionary.allTokens) {
      if (tok.path[0] !== "color") continue;
      const m = /^#([0-9A-Fa-f]{6})$/.exec(String(tok.value));
      if (!m) continue;
      definiert.add(tok.path.join("."));
      lines.push(`\\definecolor{${farbname(tok.path)}}{HTML}{${m[1].toUpperCase()}}`);
    }
    lines.push("", "% --- Semantische Dokumentfarben (claudeAI design-standards.md § 1) ---------");
    for (const [alias, pfad] of LATEX_SEMANTIK) {
      if (!definiert.has(pfad)) throw new Error(`latex/sty: Token ${pfad} fehlt fuer ${alias}`);
      lines.push(`\\colorlet{${alias}}{${farbname(pfad.split("."))}}`);
    }
    lines.push(
      "",
      "% --- Druck-Tokens: \\mnToken{<pfad>} -----------------------------------------",
      "\\newcommand*\\mnToken[1]{%",
      "  \\ifcsname mn@token@#1\\endcsname\\csname mn@token@#1\\endcsname",
      "  \\else\\PackageError{mn-design}{Unbekanntes Token '#1'}{Pfad wie in tokens/*.json, z. B. font.size.body}\\fi}",
    );
    for (const tok of dictionary.allTokens) {
      if (!LATEX_TOKEN_GRUPPEN.includes(tok.path[0])) continue;
      lines.push(`\\expandafter\\def\\csname mn@token@${tok.path.join(".")}\\endcsname{${texText(tok.value)}}`);
    }
    lines.push(
      "",
      "% --- Schriften: per Pfad aus dem Paket, nie ueber Fontconfig ---------------",
      "\\ifx\\mndsfontdir\\undefined",
      "  \\PackageError{mn-design}{\\string\\mndsfontdir\\space ist nicht gesetzt}" +
        "{Vor \\string\\usepackage{mn-design} den Schriftordner des Pakets setzen:" +
        " \\string\\def\\string\\mndsfontdir{<mn_design_system.fonts.FONT_DIR>}}",
      "\\else\\ifx\\mndsfontdir\\empty",
      "  \\PackageError{mn-design}{\\string\\mndsfontdir\\space ist leer}" +
        "{Den Schriftordner des Pakets uebergeben (mn_design_system.fonts.FONT_DIR)}",
      "\\fi\\fi",
      "% Grundschrift Geist; Kursiv ist die Editorial-Italic Source Serif 4 (font.family.italic-editorial).",
      "\\setmainfont{Geist}[Path=\\mndsfontdir/geist/, Extension=.ttf, UprightFont=*-Regular, BoldFont=*-Bold," +
        " ItalicFont=../source-serif/SourceSerif4-Italic, BoldItalicFont=../source-serif/SourceSerif4-BoldItalic]",
      "\\setsansfont{Geist}[Path=\\mndsfontdir/geist/, Extension=.ttf, UprightFont=*-Regular, BoldFont=*-Bold," +
        " ItalicFont=../source-serif/SourceSerif4-Italic, BoldItalicFont=../source-serif/SourceSerif4-BoldItalic]",
      "\\setmonofont{JetBrainsMono}[Path=\\mndsfontdir/jetbrains-mono/, Extension=.ttf, UprightFont=*-Regular," +
        " BoldFont=*-Bold, Scale=0.85]",
      "\\setmathfont{STIXTwoMath-Regular}[Path=\\mndsfontdir/stix-two/, Extension=.otf]",
      "\\newfontfamily\\mnEditorial{SourceSerif4}[Path=\\mndsfontdir/source-serif/, Extension=.ttf," +
        " UprightFont=*-Regular, BoldFont=*-Bold, ItalicFont=*-Italic, BoldItalicFont=*-BoldItalic]",
      "\\newfontfamily\\mnSymbole{NotoSansSymbols2-Regular}[Path=\\mndsfontdir/noto/, Extension=.ttf]",
      ...LATEX_SYMBOLE.map((z) => `\\newunicodechar{${z}}{{\\mnSymbole ${z}}}`),
      "\\newfontfamily\\mnGriechisch{STIXTwoMath-Regular}[Path=\\mndsfontdir/stix-two/, Extension=.otf]",
      ...LATEX_GRIECHISCH.map((z) => `\\newunicodechar{${z}}{{\\mnGriechisch ${z}}}`),
      "% Pandoc setzt fuer Aufgabenlisten $\\square$ / $\\boxtimes$ (sonst aus amssymb, das neben",
      "% unicode-math nicht geladen werden darf). unicode-math belegt die Symbole erst zu Dokumentbeginn.",
      "\\AtBeginDocument{\\providecommand*\\square{\\mdlgwhtsquare}}",
      "",
      "\\endinput",
      "",
    );
    return lines.join("\n");
  },
});

// ---------------------------------------------------------------------------
// Custom Transform: Web-Schriftnamen in CSS quoten (v0.16.0)
// ---------------------------------------------------------------------------
// "Source Serif 4" ist ungequotet kein gueltiger CSS-Familienname (die 4 ist kein
// Bezeichner) — eine Deklaration wie var(--web-font-serif-editorial, ...) wurde damit
// zur Berechnungszeit ungueltig und fiel still auf die geerbte Schrift. Nur die
// Familiennamen, nicht die Rueckfallketten web.font.stack.* (die sind schon CSS).
StyleDictionary.registerTransform({
  name: "value/web-font-quote",
  type: "value",
  filter: (token) =>
    token.path.length === 3 && token.path[0] === "web" && token.path[1] === "font",
  transform: (token) => `"${token.value}"`,
});

// ---------------------------------------------------------------------------
// Custom Filter: nur "echte" Tokens (kein _meta)
// ---------------------------------------------------------------------------
StyleDictionary.registerFilter({
  name: "no-meta",
  filter: (token) => !token.path.some((p) => p.startsWith("_")),
});

// ---------------------------------------------------------------------------
// Build
// ---------------------------------------------------------------------------
const sd = new StyleDictionary({
  source: ["tokens/**/*.json"],
  log: { verbosity: "default" },
  platforms: {
    css: {
      transforms: [...StyleDictionary.hooks.transformGroups.css, "value/web-font-quote"],
      buildPath: "dist/css/",
      files: [
        {
          destination: "tokens.css",
          format: "css/variables",
          filter: "no-meta",
          options: {
            outputReferences: false,
            selector: ":root",
          },
        },
      ],
    },
    python: {
      // S238 v0.1.0: Output direkt ins mn_design_system/-Package (statt dist/python/).
      // Damit ist tokens.py Teil des Python-Packages und via pip install -e
      // importierbar als `from mn_design_system.tokens import TOKENS`.
      transformGroup: "js",
      buildPath: "mn_design_system/",
      files: [
        {
          destination: "tokens.py",
          format: "python/dict",
          filter: "no-meta",
        },
      ],
    },
    json: {
      transformGroup: "js",
      buildPath: "dist/json/",
      files: [
        {
          destination: "tokens.json",
          format: "json/dotted",
          filter: "no-meta",
        },
      ],
    },
    // v0.21.0: Druckschicht im Paket (wie tokens.py) — dist/ liegt nicht im Wheel.
    latexsty: {
      transformGroup: "css",
      buildPath: "mn_design_system/latex/",
      files: [
        {
          destination: "mn-design.sty",
          format: "latex/sty",
          filter: "no-meta",
        },
      ],
    },
  },
});

await sd.buildAllPlatforms();

console.log("\n✓ MN PKA Design-System Build complete.");
console.log("  dist/css/tokens.css");
console.log("  dist/python/tokens.py");
console.log("  dist/json/tokens.json");
console.log("  mn_design_system/latex/mn-design.sty");
