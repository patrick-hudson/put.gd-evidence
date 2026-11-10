#!/bin/bash
set -eu
cd /home/patrick/work/scroll-integrate-1376
export DISPLAY=:137
unset WAYLAND_DISPLAY
python3 - <<'PY'
for p in ['/tmp/.X11-unix/X137','/tmp/putgd-scroll1376-xvfb']:
 n=len(p.encode());print(p,n);assert n<=107
PY
Xvfb :137 -screen 0 1280x900x24 -nolisten tcp > xvfb-e2e.log 2>&1 & xvfb=$!
echo "$xvfb" > xvfb-e2e.pid
trap 'kill "$xvfb"; wait "$xvfb" || true' EXIT
sleep 1
x11vnc -display :137 -localhost -rfbport 5937 -nopw -forever -shared > vnc-e2e.log 2>&1 & vnc=$!
echo "$vnc" > vnc-e2e.pid
trap 'kill "$vnc" "$xvfb"; wait "$vnc" "$xvfb" || true' EXIT
python3 scroll-notifications.py notifications-e2e.jsonl > notifications-peer.log 2>&1 & peer=$!
trap 'kill "$peer" "$vnc" "$xvfb"; wait "$peer" "$vnc" "$xvfb" || true' EXIT
sleep 1
python3 scroll-resident-e2e.py
python3 - <<'PY'
import json
notes=[json.loads(x) for x in open('notifications-e2e.jsonl')]
assert any('Stopped at 2,000 px' in x['body'] for x in notes),notes
print('PASS notification API received height cap warning')
PY
