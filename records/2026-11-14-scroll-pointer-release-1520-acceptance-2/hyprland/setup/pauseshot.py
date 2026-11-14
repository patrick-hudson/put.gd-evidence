#!/usr/bin/env python3
"""pauseshot.py CLI RECT OUT.png [TO X,Y]: start a capture, move the mouse through VNC, grab the screen paused, stop."""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trial import Rfb, cli
c, rect, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], sys.argv[3]
to = [int(v) for v in (sys.argv[4] if len(sys.argv) > 4 else '1500,700').split(',')]
rfb = Rfb(5900)
sid = cli(c, 'scroll.prepare', {'rect': rect})['result']['id']
cli(c, 'scroll.start', {'id': sid})
time.sleep(4)
for i in range(31):
    rfb.pointer(rfb.width // 2 + (to[0] - rfb.width // 2) * i / 30, rfb.height // 2 + (to[1] - rfb.height // 2) * i / 30)
    time.sleep(0.01)
time.sleep(1.0)
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rfbshot.py'), out], check=True)
print(json.dumps({k: cli(c, 'scroll.inspect', {'id': sid})['result'].get(k) for k in ('state', 'paused', 'pausedBy', 'height')}))
cli(c, 'scroll.stop', {'id': sid})
