#!/usr/bin/env bash
# Lädt alle benötigten Schriften aus offiziellen Quellen nach.
# Schriften werden NICHT im Repo gespeichert (Lizenz-Sauberkeit).

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$HERE/geist" "$HERE/source-serif" "$HERE/source-sans" \
         "$HERE/jetbrains-mono" "$HERE/stix-two" "$HERE/phosphor"

echo "→ Geist (Vercel · OFL 1.1)"
curl -sL -o "$HERE/geist/Geist-Regular.ttf"  https://github.com/vercel/geist-font/raw/main/fonts/geist-sans/Geist-Regular.ttf
curl -sL -o "$HERE/geist/Geist-Medium.ttf"   https://github.com/vercel/geist-font/raw/main/fonts/geist-sans/Geist-Medium.ttf
curl -sL -o "$HERE/geist/Geist-Bold.ttf"     https://github.com/vercel/geist-font/raw/main/fonts/geist-sans/Geist-Bold.ttf
curl -sL -o "$HERE/geist/Geist-Light.ttf"    https://github.com/vercel/geist-font/raw/main/fonts/geist-sans/Geist-Light.ttf

echo "→ Source Serif 4 (Adobe · OFL 1.1)"
curl -sL -o "$HERE/source-serif/SourceSerif4-Regular.ttf"     https://github.com/adobe-fonts/source-serif/raw/release/TTF/SourceSerif4-Regular.ttf
curl -sL -o "$HERE/source-serif/SourceSerif4-Italic.ttf"      https://github.com/adobe-fonts/source-serif/raw/release/TTF/SourceSerif4-Italic.ttf
curl -sL -o "$HERE/source-serif/SourceSerif4-Bold.ttf"        https://github.com/adobe-fonts/source-serif/raw/release/TTF/SourceSerif4-Bold.ttf
curl -sL -o "$HERE/source-serif/SourceSerif4-BoldItalic.ttf"  https://github.com/adobe-fonts/source-serif/raw/release/TTF/SourceSerif4-BoldItalic.ttf

echo "→ Source Sans 3 (Adobe · OFL 1.1)"
curl -sL -o "$HERE/source-sans/SourceSans3-Regular.ttf"     https://github.com/adobe-fonts/source-sans/raw/release/TTF/SourceSans3-Regular.ttf
curl -sL -o "$HERE/source-sans/SourceSans3-Italic.ttf"      https://github.com/adobe-fonts/source-sans/raw/release/TTF/SourceSans3-Italic.ttf
curl -sL -o "$HERE/source-sans/SourceSans3-Bold.ttf"        https://github.com/adobe-fonts/source-sans/raw/release/TTF/SourceSans3-Bold.ttf
curl -sL -o "$HERE/source-sans/SourceSans3-BoldItalic.ttf"  https://github.com/adobe-fonts/source-sans/raw/release/TTF/SourceSans3-BoldItalic.ttf

echo "→ JetBrains Mono (Apache 2.0)"
curl -sL -o "$HERE/jetbrains-mono/JetBrainsMono-Regular.ttf"  https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf
curl -sL -o "$HERE/jetbrains-mono/JetBrainsMono-Bold.ttf"     https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Bold.ttf

echo "→ STIX Two Math (OFL 1.1) — manuell, OTF→TTF Konversion noetig"
echo "  siehe https://github.com/stipub/stixfonts/releases"

echo "→ Phosphor Icons (MIT)"
curl -sL -o "$HERE/phosphor/Phosphor.ttf"  https://github.com/phosphor-icons/web/raw/master/src/regular/Phosphor.ttf

echo ""
echo "✓ Schriften installiert in $HERE"
echo "  Lizenz-Texte siehe CITATIONS.md"
