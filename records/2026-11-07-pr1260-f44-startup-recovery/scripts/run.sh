#!/bin/bash
# #1252 on f44's physical GNOME Wayland desktop. Runs inside dbus-run-session:
# the private session bus has no StatusNotifierWatcher, so the resident has no
# tray (f44's own session has the AppIndicator host) while its windows still
# map on the real Mutter display.
# usage: run.sh LABEL APPDIR OUT IMAGE
set -u
label=$1 appdir=$2 out=$3 image=$4
mkdir -p "$out/frames"
root=$(mktemp -d /tmp/wA.XXXXXX)
echo "$root" > "$out/root.txt"
export XDG_CONFIG_HOME=$root/c XDG_DATA_HOME=$root/d XDG_STATE_HOME=$root/s XDG_CACHE_HOME=$root/k XDG_RUNTIME_DIR=$root/r
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
socket=$XDG_RUNTIME_DIR/putgd/session.sock
printf '%s' "$socket" | wc -c > "$out/socket-bytes.txt"
[ "$(cat "$out/socket-bytes.txt")" -le 107 ] || { echo socket too long; exit 2; }
export WAYLAND_DISPLAY=/run/user/1000/wayland-0 XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=GNOME PIPEWIRE_RUNTIME_DIR=/run/user/1000
unset DISPLAY QT_QPA_PLATFORM
app=$appdir/AppRun
cli() { "$appdir/AppRun" --cli --socket "$socket" "$@" 2>/dev/null; }
[ -x "$appdir/usr/bin/putgd-cli" ] && cli() { "$appdir/usr/bin/putgd-cli" --socket "$socket" "$@" 2>/dev/null; }
wait_ready() { for i in $(seq 1 100); do cli ui.snapshot | jq -e '.result.operationsReady' >/dev/null 2>&1 && return 0; sleep 0.1; done; return 1; }
env | grep -E '^(XDG_|WAYLAND|DBUS_SESSION|PIPEWIRE)' | sort > "$out/env.txt"

# Setup pass, offscreen: save a configuration so --background takes the no-tray path.
QT_QPA_PLATFORM=offscreen "$app" --background > "$out/setup.log" 2>&1 &
setup=$!
wait_ready || { echo setup not ready; kill $setup; exit 3; }
doc=$(cli settings.developmentTemplate | jq -c '.result.document')
cli settings.save "{\"document\":$doc,\"expectedRevision\":\"\"}" > "$out/settings-save.json"
cli ui.quit > /dev/null; wait $setup
rm -f "$socket"

# The run: a background resident with no tray, the editor opened at about 3 s.
python3 "$(dirname "$0")/frames.py" 5901 "$out/frames" 22 > "$out/frames.log" 2>&1 &
frames=$!
sleep 0.5
t0=$(date +%s.%N); echo "$t0" > "$out/t0.txt"
"$app" --background > "$out/resident.log" 2>&1 &
resident=$!; echo $resident > "$out/resident.pid"
wait_ready || echo "not ready" >> "$out/notes.txt"
sleep 2.5
opened_at=$(date +%s.%N)
cli editor.open "{\"source\":\"file\",\"path\":\"$image\"}" > "$out/editor-open.json"
echo "$opened_at" > "$out/editor-open-at.txt"
id=$(jq -r '.result.operationId' "$out/editor-open.json")
for i in $(seq 1 19); do
  now=$(date +%s.%N)
  cli ui.snapshot | jq -c --arg t "$(echo "$now - $t0" | bc)" '{t:($t|tonumber),ui:.result.diagnostics.ui,trayAvailable:.result.diagnostics.trayAvailable}' >> "$out/ui-timeline.jsonl"
  cli editor.inspect "{\"id\":\"$id\"}" | jq -c --arg t "$(echo "$now - $t0" | bc)" '{t:($t|tonumber),phase:.result.phase,error:.error.code}' >> "$out/editor-timeline.jsonl"
  echo "-- t=$(echo "$now - $t0" | bc)" >> "$out/children.txt"; ps -eo pid=,ppid=,args= | grep -F "$appdir/usr/bin/" | grep -v grep | cut -c1-200 >> "$out/children.txt"
  sleep 0.9
done
wait $frames
cli editor.cancel "{\"id\":\"$id\"}" > "$out/editor-cancel.json"
sleep 1
cli ui.quit > "$out/quit.json"
for i in $(seq 1 50); do kill -0 $resident 2>/dev/null || break; sleep 0.1; done
kill -0 $resident 2>/dev/null && { echo "resident still running; TERM" >> "$out/notes.txt"; kill $resident; }
cp -r "$root/s" "$out/state" 2>/dev/null
echo done > "$out/done"
