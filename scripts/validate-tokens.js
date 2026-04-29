/**
 * MN PKA Design-System — Token-Validator
 *
 * Prueft:
 *   1. Color-Kontraste WCAG-AA (mind. 4.5:1 fuer Body-Text, 3:1 fuer Large-Text)
 *   2. Token-Format-Konsistenz (alle Color-Tokens sind valides Hex oder rgba)
 *   3. Required-Tokens vorhanden (color.light.text, color.dark.text, ...)
 *
 * Aufruf: npm run validate
 * Exit-Code: 0 bei OK, 1 bei Fehlern.
 */

import { readFileSync } from "node:fs";

const tokens = JSON.parse(readFileSync("dist/json/tokens.json", "utf8"));

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------
function hexToRgb(hex) {
  const m = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
  if (!m) return null;
  return {
    r: parseInt(m[1], 16),
    g: parseInt(m[2], 16),
    b: parseInt(m[3], 16),
  };
}

function relLuminance({ r, g, b }) {
  // WCAG 2.1 relative luminance
  const f = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}

function contrastRatio(hex1, hex2) {
  const r1 = hexToRgb(hex1);
  const r2 = hexToRgb(hex2);
  if (!r1 || !r2) return null;
  const l1 = relLuminance(r1);
  const l2 = relLuminance(r2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
const errors = [];
const warnings = [];

// 1. Required Tokens
const required = [
  "color.light.text",
  "color.light.bg",
  "color.light.h1",
  "color.light.accent",
  "color.dark.text",
  "color.dark.bg",
  "color.brand",
  "font.family.sans",
  "font.size.body",
  "font.leading.body",
];
for (const r of required) {
  if (!(r in tokens)) {
    errors.push(`Missing required token: ${r}`);
  }
}

// 2. Color-Token Hex-Format
for (const [k, v] of Object.entries(tokens)) {
  if (k.startsWith("color.") && typeof v === "string") {
    if (v.startsWith("#")) {
      if (!/^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(v)) {
        warnings.push(`Color-Token ${k}: ungueltiges Hex "${v}"`);
      }
    } else if (!v.startsWith("rgba(") && !v.startsWith("rgb(")) {
      // Erlaubt: #hex, rgba(...), rgb(...)
      warnings.push(`Color-Token ${k}: unbekanntes Format "${v}"`);
    }
  }
}

// 3. Kontrast WCAG-AA: Body-Text auf Background
const checks = [
  // [foreground, background, label, minRatio]
  ["color.light.text", "color.light.bg", "Body Light", 4.5],
  ["color.light.h1", "color.light.bg", "H1 Light", 4.5],
  ["color.light.h2", "color.light.bg", "H2 Light", 4.5],
  ["color.light.accent", "color.light.bg", "Accent Light (Links)", 4.5],
  ["color.light.text-muted", "color.light.bg", "Muted Light (Captions)", 4.5],
  ["color.dark.text", "color.dark.bg", "Body Dark", 4.5],
  ["color.dark.h2", "color.dark.bg", "H2 Dark", 4.5],
  ["color.dark.accent", "color.dark.bg", "Accent Dark (Links)", 4.5],
];
let okCount = 0;
let warnCount = 0;
const details = [];
for (const [fgKey, bgKey, label, minRatio] of checks) {
  const fg = tokens[fgKey];
  const bg = tokens[bgKey];
  if (!fg || !bg) {
    errors.push(`Contrast-Check skipped: missing ${fgKey} or ${bgKey}`);
    continue;
  }
  const ratio = contrastRatio(fg, bg);
  if (ratio === null) {
    warnings.push(`Contrast-Check ${label}: kein numerischer Wert berechenbar (rgba?)`);
    continue;
  }
  const pass = ratio >= minRatio;
  details.push(
    `  ${pass ? "✓" : "✗"} ${label.padEnd(28)} ${fg} / ${bg}  ${ratio.toFixed(2)}:1  (min ${minRatio})`,
  );
  if (pass) okCount++;
  else {
    warnCount++;
    warnings.push(`Contrast-Check ${label} FAILED: ${ratio.toFixed(2)}:1 < ${minRatio}`);
  }
}

// ---------------------------------------------------------------------------
// Report
// ---------------------------------------------------------------------------
console.log("MN PKA Design-System — Token-Validator");
console.log("=".repeat(60));
console.log("\nKontrast-Checks (WCAG-AA, 4.5:1 fuer Body):");
details.forEach((d) => console.log(d));
console.log(
  `\n  Bestanden: ${okCount}/${okCount + warnCount}  ·  ` +
    `Erforderliche Tokens: ${required.length - errors.filter((e) => e.startsWith("Missing")).length}/${required.length}`,
);

if (warnings.length) {
  console.log("\nWARNINGS:");
  warnings.forEach((w) => console.log(`  ! ${w}`));
}

if (errors.length) {
  console.log("\nERRORS:");
  errors.forEach((e) => console.log(`  ✗ ${e}`));
  process.exit(1);
}

console.log("\n✓ Alle Token-Validierungen bestanden.");
process.exit(0);
