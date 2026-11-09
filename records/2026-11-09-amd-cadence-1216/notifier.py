#!/usr/bin/env python3
"""#1216: keep a timed (timeout-bar) Plasma notification on screen until the stop file appears; close what it sent."""
import json, os, re, subprocess, sys, time
from pathlib import Path
stop = Path(sys.argv[1]); out = Path(sys.argv[2]); every = float(sys.argv[3]); expire = int(sys.argv[4])
env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
def bus(*a):
    return subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.freedesktop.Notifications', '--object-path', '/org/freedesktop/Notifications', '--method'] + list(a), env=env, capture_output=True, text=True, timeout=10)
ids, log = [], []
n = 0
while not stop.exists():
    n += 1
    r = bus('org.freedesktop.Notifications.Notify', '1216-probe', '0', '', '1216 cadence probe', 'transient popup %d' % n, '[]', '{}', str(expire))
    m = re.search(r'uint32 (\d+)', r.stdout)
    if m: ids.append(int(m.group(1)))
    log.append({'t': time.time(), 'id': int(m.group(1)) if m else None, 'rc': r.returncode, 'err': r.stderr.strip()[:200]})
    time.sleep(every)
for i in ids:
    bus('org.freedesktop.Notifications.CloseNotification', str(i))
out.write_text(json.dumps({'sent': len(ids), 'failed': sum(1 for l in log if l['rc']), 'log': log}, indent=1) + '\n')
