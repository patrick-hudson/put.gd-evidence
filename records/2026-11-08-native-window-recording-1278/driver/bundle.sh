#!/bin/bash
# bundle.sh OUT RUN... : copy each run's JSON, helper log and one frame strip per case into OUT/<run name>.
set -u
out=$1; shift; mkdir -p "$out"
for run in "$@"; do
  name=$(basename "$run"); dest="$out/$name"; mkdir -p "$dest"
  cp "$run"/*.json "$dest"/ 2>/dev/null
  [ -f "$run/logs/record-debug.log" ] && grep -v "rate window" "$run/logs/record-debug.log" > "$dest/record-debug.log"
  for c in $(ls "$run/frames" 2>/dev/null | sed -n 's/^\(.*\)-0[0-9]\.png$/\1/p' | sort -u); do
    inputs=(); for f in "$run/frames/$c"-0*.png; do inputs+=(-i "$f"); done
    n=$((${#inputs[@]} / 2))
    filter=""; for i in $(seq 0 $((n-1))); do filter+="[$i]scale=-2:240[s$i];"; done
    for i in $(seq 0 $((n-1))); do filter+="[s$i]"; done
    ffmpeg -v error "${inputs[@]}" -filter_complex "${filter}hstack=$n" -y "$dest/$c.png"
  done
done
du -sh "$out"
