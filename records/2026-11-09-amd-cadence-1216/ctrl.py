#!/usr/bin/env python3
"""#1216 control: fixture frame clock alone (no recorder), with and without a timed notification on screen."""
import json, subprocess, sys, time
from pathlib import Path
R = Path.home() / 'i1216'
sys.path.insert(0, str(R / 'tools/lab'))
import record_run, fluidity
env, _ = record_run.session_environment()
env['PIPEWIRE_RUNTIME_DIR'] = '/run/user/1000'
out = R / 'ctrl'; out.mkdir(exist_ok=True)
results = []
for n, popup in enumerate([False, True, True, False], 1):
    stop = R / ('ctrl%d.stop' % n)
    notifier = None
    if popup:
        notifier = subprocess.Popen([sys.executable, str(R / 'notifier.py'), str(stop), str(out / ('notifier-%d.json' % n)), '3', '7000'], stdin=subprocess.DEVNULL)
        time.sleep(4)
    ticks = out / ('ticks-%d-%s.log' % (n, 'popup' if popup else 'clean'))
    p = subprocess.Popen([sys.executable, str(R / 'tools/lab/fluidity.py'), 'fixture', '--seconds', '13', '--ticks', str(ticks), '--output', '1920x1080+0+0'], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    line = p.stdout.readline()
    p.wait(40)
    times = [int(l.split()[1]) for l in ticks.read_text().splitlines() if l and not l.startswith('#')]
    if notifier:
        stop.touch()
        notifier.wait(30)
    rep = fluidity.ticks_report(str(ticks), 60, times[0] + 2_000_000, None)
    results.append({'n': n, 'popup': popup, 'placement': line.strip()[:120], 'fps': round(1000 / rep['meanMs'], 2), 'report': rep})
    print(results[-1]['n'], 'popup' if popup else 'clean', results[-1]['fps'], rep['missedFrames'], flush=True)
    time.sleep(2)
(out / 'results.json').write_text(json.dumps(results, indent=1) + '\n')
