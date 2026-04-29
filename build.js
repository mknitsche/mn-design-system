/**
 * MN PKA Design-System — Build Script
 *
 * Liest Tokens aus tokens/*.json (alle automatisch), generiert:
 *   dist/css/tokens.css      — CSS Custom Properties (Web)
 *   dist/python/tokens.py    — Python-Dict (claudeAI ReportLab)
 *   dist/json/tokens.json    — flach, fuer beliebige Konsumenten
 *   dist/latex/tokens.tex    — \def-Macros (LaTeX-Paper)
 *
 * Aufruf: npm run build
 */

import StyleDictionary from "style-dictionary";

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
// Custom Format: LaTeX
// ---------------------------------------------------------------------------
StyleDictionary.registerFormat({
  name: "latex/macros",
  format: ({ dictionary, file }) => {
    const lines = [
      `% ${file?.comment || "MN PKA Design-System Tokens — auto-generiert."}`,
      "% Auto-generiert aus tokens/*.json via Style Dictionary.",
      "% NICHT MANUELL BEARBEITEN — Aenderungen werden ueberschrieben.",
      "",
    ];
    for (const tok of dictionary.allTokens) {
      const macroName = tok.path.join("").replace(/[^A-Za-z0-9]/g, "");
      const val = String(tok.value);
      lines.push(`\\def\\mnpka${macroName}{${val}}`);
    }
    lines.push("");
    return lines.join("\n");
  },
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
      transformGroup: "css",
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
      transformGroup: "js",
      buildPath: "dist/python/",
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
    latex: {
      transformGroup: "css",
      buildPath: "dist/latex/",
      files: [
        {
          destination: "tokens.tex",
          format: "latex/macros",
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
console.log("  dist/latex/tokens.tex");
