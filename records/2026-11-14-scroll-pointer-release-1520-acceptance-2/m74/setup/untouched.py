#!/usr/bin/env python3
"""untouched.py CLI RECT URL PROFILE LABEL: one capture nobody touches; prints its end, height, steps and time."""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trial import cli,cursorpos
c, rect, url, profile, label = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], sys.argv[3], sys.argv[4], sys.argv[5]
subprocess.run(['firefox', '--profile', profile, url], capture_output=True)
time.sleep(6)
subprocess.run(['xdotool','mousemove','300','100'],check=True);time.sleep(.2)
position_before=cursorpos()
began = time.monotonic()
sid = cli(c, 'scroll.prepare', {'rect': rect})['result']['id']
cli(c, 'scroll.start', {'id': sid})
view = {}
while time.monotonic() - began < 240:
    view = cli(c, 'scroll.inspect', {'id': sid}).get('result', {})
    if view.get('state') in ('done', 'failed', 'cancelled'):
        break
    time.sleep(1)
r = view.get('result', {})
print(json.dumps({'label': label, 'id': sid, 'state': view.get('state'), 'endReason': view.get('endReason'), 'height': view.get('height'),
                  'steps': view.get('steps'), 'elapsedMs': view.get('elapsedMs'), 'wallSeconds': round(time.monotonic() - began, 1), 'sha256': r.get('sha256'), 'pointerBefore':position_before,'pointerAfter':cursorpos()}))
