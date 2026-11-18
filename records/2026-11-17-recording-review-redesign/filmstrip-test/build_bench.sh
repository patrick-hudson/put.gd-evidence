#!/usr/bin/env bash
set -euo pipefail
lib="$PWD/squashfs-root/usr/lib"
g++ -std=c++20 -O2 -Wall -Wextra bench.cpp -o bench $(pkg-config --cflags Qt6Gui) \
  -I FFmpeg-946fcce07b6dcd0331c8cc609192aeff5e1924f8 \
  -L "$lib" -Wl,-rpath-link,"$lib" '-Wl,-rpath,$ORIGIN/squashfs-root/usr/lib' \
  -l:libQt6Gui.so.6 -l:libQt6Core.so.6 -l:libavformat.so.63 -l:libavcodec.so.63 \
  -l:libswscale.so.10 -l:libavutil.so.61
