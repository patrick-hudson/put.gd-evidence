#!/bin/bash
# Headless acceptance: start the resident offscreen on a private bus, open the
# editor on real captures through putgd-cli, apply highlights, save copies.
set -u
BUILD="$1"; CAPS="$2"; OUT="$3"
mkdir -p "$OUT"
ROOT=/tmp/i1237hl; rm -rf "$ROOT"; mkdir -p "$ROOT/run" "$ROOT/cfg" "$ROOT/data" "$ROOT/cache" "$ROOT/state"; chmod 700 "$ROOT/run"
export XDG_RUNTIME_DIR="$ROOT/run" XDG_CONFIG_HOME="$ROOT/cfg" XDG_DATA_HOME="$ROOT/data" XDG_CACHE_HOME="$ROOT/cache" XDG_STATE_HOME="$ROOT/state"
export QT_QPA_PLATFORM=offscreen PUTGD_STARTED_FOR_UPLOAD=1
unset DISPLAY WAYLAND_DISPLAY XDG_SESSION_TYPE XDG_CURRENT_DESKTOP
cd "$ROOT"
"$BUILD/putgd" --background > "$OUT/resident.log" 2>&1 &
RES=$!
SOCK="$XDG_RUNTIME_DIR/putgd/session.sock"
for i in $(seq 1 100); do [ -S "$SOCK" ] && break; sleep 0.2; done
CLI="$BUILD/putgd-cli --socket $SOCK"
$CLI capabilities > "$OUT/capabilities.json" 2>&1
run_case() {  # name file command-json...
  local name="$1" file="$2"; shift 2
  [ -n "${ONLY:-}" ] && [ "$ONLY" != "$name" ] && return
  local open id
  for i in $(seq 1 60); do
    open=$($CLI editor.open "{\"source\":\"file\",\"path\":\"$file\"}" 2>&1)
    id=$(python3 -c "import json,sys;r=json.loads(sys.argv[1]).get('result',{});print(r.get('operationId') or r.get('operation',{}).get('id') or '')" "$open" 2>/dev/null)
    [ -n "$id" ] && break; sleep 0.5
  done
  echo "$name open: $(echo "$open" | cut -c1-160)" >> "$OUT/log.txt"
  [ -z "$id" ] && return
  local n=0
  for command in "$@"; do
    n=$((n+1)); local applied
    for i in $(seq 1 50); do applied=$($CLI editor.apply "{\"id\":\"$id\",\"commands\":[$command]}" 2>&1); echo "$applied" | grep -q editor_starting || break; sleep 0.3; done
    echo "$name apply $n: $(echo "$applied" | cut -c1-200)" >> "$OUT/log.txt"
  done
  $CLI editor.inspect "{\"id\":\"$id\"}" > "$OUT/$name.inspect.json" 2>&1
  local saved; saved=$($CLI editor.saveCopy "{\"id\":\"$id\",\"path\":\"$OUT/$name.png\",\"overwrite\":true}" 2>&1); echo "$name save: $(echo "$saved" | cut -c1-120)" >> "$OUT/log.txt"
  $CLI editor.cancel "{\"id\":\"$id\"}" > /dev/null 2>&1
}
# Cinnamon Update Manager (light, LCD text): drag snap, word, line, colours.
run_case cinnamon "$CAPS/cinnamon.png" \
 '{"op":"add","shape":{"kind":"highlight","rect":[400,276,520,8],"snap":"text"}}' \
 '{"op":"add","shape":{"kind":"highlight","at":[500,545],"snap":"word","color":"#22c55e"}}' \
 '{"op":"add","shape":{"kind":"highlight","at":[450,561],"snap":"line","color":"#3b82f6"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[394,574,520,6],"snap":"text","color":"#ec4899"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[840,655,120,30],"snap":"none","color":"#111317"}}'
# put.gd History (dark zebra table): drag across two rows, a word in a cell, a line.
run_case history "$CAPS/history.png" \
 '{"op":"add","shape":{"kind":"highlight","rect":[150,240,560,60],"snap":"text"}}' \
 '{"op":"add","shape":{"kind":"highlight","at":[410,327],"snap":"word","color":"#3b82f6"}}' \
 '{"op":"add","shape":{"kind":"highlight","at":[200,365],"snap":"line","color":"#22c55e"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[120,55,300,30],"snap":"text","color":"#ffffff"}}'
# Plasma notification (white on navy) and Kubuntu wallpaper lettering.
run_case plasma "$CAPS/plasma.png" \
 '{"op":"add","shape":{"kind":"highlight","at":[1000,655],"snap":"line"}}' \
 '{"op":"add","shape":{"kind":"highlight","at":[950,675],"snap":"word","color":"#22c55e"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[560,425,250,40],"snap":"none"}}'
# Aurora: a notice over a painting, the painting itself (fallback), the red label.
run_case aurora "$CAPS/aurora.png" \
 '{"op":"add","shape":{"kind":"highlight","at":[1230,264],"snap":"line"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[120,480,400,100],"snap":"none"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[120,600,400,100],"snap":"none","color":"#3b82f6"}}' \
 '{"op":"add","shape":{"kind":"highlight","rect":[215,400,335,30],"snap":"none"}}'
kill $RES 2>/dev/null; wait $RES 2>/dev/null
echo done >> "$OUT/log.txt"
