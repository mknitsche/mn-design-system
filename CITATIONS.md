# Citations & Licenses

Lizenzen + Quellenangaben aller verwendeten Schriften, Symbole und Inspirationsquellen.

## Schriften

### Geist Sans
- **Designer:** Vercel Inc.
- **Lizenz:** SIL Open Font License 1.1
- **URL:** https://github.com/vercel/geist-font
- **Verwendung:** Body, Headlines, UI

### Source Serif 4
- **Designer:** Frank Grießhammer (Adobe)
- **Erstveröffentlichung:** 2014, Version 4 in 2021
- **Lizenz:** SIL Open Font License 1.1
- **URL:** https://github.com/adobe-fonts/source-serif
- **Verwendung:** Editorial Italic, Drop-Caps, Bibel-Zitate

### Source Sans 3
- **Designer:** Paul D. Hunt (Adobe)
- **Erstveröffentlichung:** 2012, Version 3 in 2021
- **Lizenz:** SIL Open Font License 1.1
- **URL:** https://github.com/adobe-fonts/source-sans
- **Verwendung:** Stack D Alternative

### JetBrains Mono
- **Designer:** JetBrains s.r.o.
- **Lizenz:** SIL Open Font License 1.1 (laut Schriftdatei, Version 2.211; Text in `mn_design_system/fonts/jetbrains-mono/OFL.txt`)
- **URL:** https://www.jetbrains.com/lp/mono/
- **Verwendung:** Code, Mono-Kicker, ISBN-Block

### STIX Two Text / STIX Two Math
- **Maintainer:** The STIX Fonts Project (STI Pub Companies)
- **Lizenz:** SIL Open Font License 1.1 — STIX Two Text und STIX Two Math, beide Version 2.13 (Release `v2.13b171`; Math seit 0.16.1, vorher Version 2.02 unter der STIX Fonts User License). Text des Upstream-Projekts in `mn_design_system/fonts/stix-two/OFL.txt`. Die STIX-Two-Text-Dateien sind Teilmengen (Subsets, z. B. 285 Glyphen in Regular) der Upstream-Fassung; STIX Two Math liegt vollstaendig bei
- **URL:** https://github.com/stipub/stixfonts
- **Verwendung:** Griechisch-/Mathe-Rueckfall (σ), mathematische Notation

### Inter
- **Designer:** Rasmus Andersson (The Inter Project Authors)
- **Lizenz:** SIL Open Font License 1.1 (`mn_design_system/fonts/inter/OFL.txt`)
- **URL:** https://github.com/rsms/inter
- **Verwendung:** alternative Grotesk (Familie registriert, kein Standard-Slot)

### Noto Sans / Noto Sans Symbols 2
- **Herausgeber:** The Noto Project Authors (Google)
- **Lizenz:** SIL Open Font License 1.1 (`mn_design_system/fonts/noto/OFL.txt`)
- **URL:** https://github.com/notofonts
- **Verwendung:** registriert, kein Standard-Slot (Familie fuer Fett/Kursiv angemeldet)

## Symbole

### Phosphor Icons
- **Designer:** Tobias Fried & Helena Zhang
- **Lizenz:** MIT License
- **URL:** https://phosphoricons.com/
- **Verwendung:** UI-Symbole (PUA E000–F8FF), insgesamt 1.512 Glyphen in 6 Stilen
- **Beispiel:** `caret-right` (U+E13A) als Bullet-Glyph

## Bibliotheken im Paket

### Apache ECharts 6.1.0
- Apache ECharts 6.1.0 — Apache License 2.0 — https://echarts.apache.org
- **Projekt:** Apache Software Foundation
- **Verwendung:** Zeitreihen-Diagramm (`verlauf_chart`); ausgeliefert wird der Build `echarts.common.min.js`, unveraendert aus dem npm-Tarball (Pin, SHA-256 und Tarball-Integrity in `mn_design_system/vendor/echarts/VENDOR.json`)
- **Im Paket:** `mn_design_system/vendor/echarts/` mit `LICENSE` und `NOTICE` des Upstream-Projekts; Apache-2.0 verlangt, beides bei jeder Weitergabe mitzugeben

## Inspirations- und Referenzwerke

- **Tufte, E. R.** (1983/1990). *The Visual Display of Quantitative Information* / *Envisioning Information*. Graphics Press.
- **Lupton, E.** (2010). *Thinking with Type*. Princeton Architectural Press.
- **Bringhurst, R.** (2004). *The Elements of Typographic Style*. Hartley & Marks.
- **Müller-Brockmann, J.** (1981). *Grid Systems in Graphic Design*. Niggli.

## Tools

- **Style Dictionary** (Amazon, Apache 2.0) — Token-Build-Pipeline
- **pyphen** (LGPL/MPL/GPL) — deutsche Silbentrennung
- **WCAG 2.2** (W3C Recommendation 2023) — Kontrast-Richtlinien

## Schriftdateien im Paket

Die Schriftdateien liegen im Paket unter `mn_design_system/fonts/<familie>/`, je Familie mit ihrem Lizenztext (`OFL.txt` bzw. `LICENSE` fuer Phosphor). Seit 0.16.0 prueft ein Test, dass keine Familie ohne Lizenztext ausgeliefert wird.

## Was nicht im Repo lebt

- **Logo-Files** (Matthias-Nitsche-Fotografie + PKA-Brand) sind proprietär.
