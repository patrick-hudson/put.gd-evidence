#!/bin/bash
set -euo pipefail
p=$(dirname "$0")
d="$p/2026-11-23-unhinged-mode-acceptance"
for h in m74 f44 d69 k72 aurora-amd; do
  case "$h" in
    m74) lab='Linux Mint 22.3 · Cinnamon X11'; x=984;;
    f44) lab='Fedora 44 · GNOME Wayland'; x=979;;
    d69) lab='Debian 13 · Plasma Wayland'; x=979;;
    k72) lab='Kubuntu 26.04 · Plasma Wayland'; x=979;;
    aurora-amd) lab='Aurora Fedora 45 · Plasma Wayland'; x=979;;
  esac
  for state in A B; do
    src="$d/$h/settings-$state.png"
    test -s "$src" || continue
    label='Unhinged mode: off by default'
    [[ "$state" == A ]] || label='Unhinged mode: on'
    width=$(magick identify -format '%w' "$src")
    magick "$src" -crop "${width}x700+0+115" +repage \
      -fill none -stroke '#D7263D' -strokewidth 3 \
      -draw "roundrectangle $((x-16)),466 $((x+16)),501 5,5" \
      -stroke none -fill '#D7263D' -font /usr/share/fonts/open-sans/OpenSans-Bold.ttf -pointsize 19 \
      -annotate "+$((x+32))+490" "$label" \
      -background '#f3f5f5' -gravity south -splice 0x48 -gravity southwest \
      -fill '#212424' -font /usr/share/fonts/open-sans/OpenSans-Regular.ttf -pointsize 18 -annotate +20+15 \
      "$h · $lab · 26.1123.6699-dev+ga773c51e5947" "$d/$h/annotated-$state.png"
  done
done
