#!/usr/bin/env python3
"""qmp_early.py RUN DELAY_MS STEP_MS STEPS X1 Y1 X2 Y2 [--keys=ctrl,shift,f9] [--no-key] [--hold-ms=N]

On the QEMU host: the region hotkey as real key events, then a tablet drag on head 0
(1280x800), all on one QMP connection so the delays are the ones asked for. Prints the
timings as JSON. The pointer is placed at X1,Y1 (with a nudge) a second before the key.
"""
import json, math, os, sys, time
sys.path.insert(0, os.path.join(os.environ.get('W3_ROOT', os.path.expanduser('~/work/w3-1487')), 'tools/lab'))
import lab  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '1') for a in sys.argv[1:] if a.startswith('--'))
run, delay, step, steps = args[0], int(args[1]), int(args[2]), int(args[3])
x1, y1, x2, y2 = map(float, args[4:8])
keys = opts.get('keys', 'ctrl,shift,f9').split(','); W, H = 1280, 800

def tablet(x, y):
    return [{'type': 'abs', 'data': {'axis': 'x', 'value': min(32767, math.ceil(x * 32768 / W))}},
            {'type': 'abs', 'data': {'axis': 'y', 'value': min(32767, math.ceil(y * 32768 / H))}}]

with lab.QMP(os.path.join(run, 'qmp.sock')) as q:
    send = lambda events: q.execute('input-send-event', {'events': events, 'device': 'video0', 'head': 0})
    send(tablet(x1 - 4, y1 - 4)); time.sleep(0.2); send(tablet(x1, y1)); time.sleep(1.0)
    t0 = time.monotonic(); out = {}
    if 'no-key' not in opts:
        q.execute('input-send-event', {'events': [{'type': 'key', 'data': {'down': True, 'key': {'type': 'qcode', 'data': k}}} for k in keys]})
        time.sleep(0.05)
        q.execute('input-send-event', {'events': [{'type': 'key', 'data': {'down': False, 'key': {'type': 'qcode', 'data': k}}} for k in reversed(keys)]})
    out['keyUpMs'] = round((time.monotonic() - t0) * 1000, 1)
    time.sleep(max(0, delay / 1000 - (time.monotonic() - t0)))
    send(tablet(x1, y1) + [{'type': 'btn', 'data': {'button': 'left', 'down': True}}])
    out['pressMs'] = round((time.monotonic() - t0) * 1000, 1)
    if 'hold-ms' in opts: time.sleep(int(opts['hold-ms']) / 1000)
    for i in range(1, steps + 1):
        time.sleep(step / 1000)
        send(tablet(x1 + (x2 - x1) * i / steps, y1 + (y2 - y1) * i / steps))
    send([{'type': 'btn', 'data': {'button': 'left', 'down': False}}])
    out['releaseMs'] = round((time.monotonic() - t0) * 1000, 1)
print(json.dumps(out))
