#!/bin/bash
# live4k.sh OUT : #1808 live Copy text on a 3840x2160 KWin Wayland desktop (nested, virtual output) on k72.
# Runs the installed put.gd package's resident; captures the whole monitor through KWin, recognizes, copies.
set -u
OUT=$1; mkdir -p "$OUT"; cd "$OUT"
if [ "${INNER:-}" != 1 ]; then
  mkdir -p rt && chmod 700 rt
  export XDG_RUNTIME_DIR=$PWD/rt
  INNER=1 exec dbus-run-session -- bash "$0" "$OUT"
fi
export XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=KDE KDE_FULL_SESSION=true KDE_SESSION_VERSION=6 XDG_MENU_PREFIX=plasma-
kbuildsycoca6 --noincremental > sycoca0.log 2>&1
kwin_wayland --virtual --width 3840 --height 2160 --no-lockscreen --no-global-shortcuts --socket wl-i1808 > kwin.log 2>&1 &
KWIN=$!
for i in $(seq 100); do [ -S "$XDG_RUNTIME_DIR/wl-i1808" ] && break; sleep 0.1; done
export WAYLAND_DISPLAY=$XDG_RUNTIME_DIR/wl-i1808 QT_QPA_PLATFORM=wayland
plasmashell > plasmashell.log 2>&1 &
sleep 6
# Known text in two real windows.
seq -f "Line %03g: a careful reader checks each sample beside the river today." 1 60 > left.txt
python3 -c "
import textwrap
words='the quick brown fox jumps over the lazy dog while seven bright owls watch from the old oak tree'.split()
print('\n'.join(' '.join(words[(i*3)%len(words):]+words[:(i*3)%len(words)]) for i in range(60)))" > right.txt
kwrite left.txt > kwrite1.log 2>&1 &
konsole --hide-menubar -e less right.txt > konsole.log 2>&1 &
sleep 6
mkdir -p cfg data cache state
export XDG_CONFIG_HOME=$PWD/cfg XDG_DATA_HOME=$PWD/data XDG_CACHE_HOME=$PWD/cache XDG_STATE_HOME=$PWD/state
# KWin offers ScreenShot2 only to an executable whose entry matches; put.gd checks XDG_DATA_HOME too.
mkdir -p data/applications && cp /usr/share/applications/putgd.desktop data/applications/
kbuildsycoca6 --noincremental > sycoca.log 2>&1
/usr/bin/putgd --background > resident.log 2>&1 &
for i in $(seq 60); do /usr/bin/putgd-cli capabilities '{}' > caps.json 2>/dev/null && grep -q '"ok": *true' caps.json && break; sleep 1; done
python3 -I - <<'EOF' > result.json
import json, os, subprocess, threading, time
from pathlib import Path
def cli(m, p):
    r = subprocess.run(['/usr/bin/putgd-cli', m, json.dumps(p)], capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout)
peak = {}
stop = threading.Event()
def watch():
    while not stop.is_set():
        for p in os.listdir('/proc'):
            if not p.isdigit(): continue
            try:
                if Path(f'/proc/{p}/comm').read_text().strip() != 'putgd-ocr': continue
                for l in Path(f'/proc/{p}/status').read_text().splitlines():
                    if l.startswith('VmHWM:'): peak[p] = max(peak.get(p, 0), int(l.split()[1]))
                    if l.startswith('Threads:'): peak['threads_' + p] = max(peak.get('threads_' + p, 0), int(l.split()[1]))
            except OSError: pass
        time.sleep(0.01)
t = threading.Thread(target=watch, daemon=True); t.start()
start = time.monotonic()
op = cli('text.recognize', {'source': 'monitor', 'copy': True})
oid = (op.get('result') or {}).get('operationId')
while oid:
    r = cli('text.inspect', {'id': oid})
    if (r.get('result') or {}).get('state') in ('completed', 'failed', 'cancelled'): break
    time.sleep(0.05)
wall = time.monotonic() - start
time.sleep(0.2); stop.set(); t.join()
res = (r.get('result') or {}) if oid else op
print(json.dumps({'op': op, 'wallSeconds': round(wall, 3), 'helper': peak, 'inspect': res}, ensure_ascii=False, indent=1))
EOF
wl-paste --no-newline > pasted.txt 2>wl-paste.err
python3 -I -c "
import json; r=json.load(open('result.json'))['inspect']; t=r.get('text','')
p=open('pasted.txt',encoding='utf-8').read()
print(json.dumps({'state':r.get('state'),'error':r.get('error'),'characterCount':r.get('characterCount'),'copyStatus':r.get('copyStatus'),'truncated':r.get('truncated'),'timings':r.get('timings'),'pastedEqualsText':p==t,'pastedChars':len(p),
'leftLinesFound':sum(1 for l in open('left.txt') if l.strip() in t),'rightLinesFound':sum(1 for l in open('right.txt') if l.strip() in t)}))" > summary.json
timeout 20 spectacle -b -n -f -o "$PWD/frame.png" > spectacle.log 2>&1
cat summary.json
/usr/bin/putgd-cli ui.quit '{}' > /dev/null 2>&1
sleep 3
kill $KWIN
