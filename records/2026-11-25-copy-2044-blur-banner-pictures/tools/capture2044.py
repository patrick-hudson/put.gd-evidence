#!/usr/bin/env python3
"""#2044: the recording review's blur banner, before and after. Run on m74 under desktop_lock.py run.
A private resident records 3 s of a desktop region, opens private review, arms Blur and frames the desktop."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib2044 import Run  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument('--build', required=True)
p.add_argument('--run', required=True)
p.add_argument('--label', required=True)
a = p.parse_args()
R = Run(a.build, a.run, a.label)
rid = None
try:
    R.start()
    prepared = R.cli('recording.prepare', {'target': {'kind': 'region', 'rect': [200, 150, 960, 540]}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}})
    R.say('prepare', json.dumps(prepared)[:300])
    rid = prepared['result']['recordingId']
    state = lambda: R.cli('recording.inspect', {'id': rid}).get('result', {}).get('state')
    assert R.until(lambda: state() == 'ready', 120), 'not ready: %s' % state()
    R.cli('recording.start', {'id': rid})
    for step in range(6):
        R.x('xdotool', 'mousemove', str(300 + step * 120), str(300 + step * 40))
        time.sleep(0.5)
    R.say('stop', json.dumps(R.cli('recording.stop', {'id': rid}, timeout=60))[:300])
    assert R.until(lambda: state() == 'reviewing', 120), 'not reviewing'
    review = R.cli('recording.review', {'id': rid, 'action': 'inspect'})
    R.say('review open', review['ok'], review.get('error'))
    wins = R.until(lambda: [w for w in R.windows() if 'eview' in w[1]], 30)
    R.say('windows', R.windows())
    if wins:
        R.place(wins[0][0], 160, 60, 1280, 860)
    R.park()
    R.frame('review-idle', settle=1.5)
    armed = R.cli('recording.review', {'id': rid, 'action': 'armBlur'})
    R.facts['armBlur'] = {'warning': armed.get('result', {}).get('warning'), 'blurGuidance': armed.get('result', {}).get('blurGuidance')}
    R.say('armBlur', json.dumps(R.facts['armBlur']))
    R.park()
    R.frame('blur-armed', settle=1.5)
    st = lambda: R.cli('recording.review', {'id': rid, 'action': 'inspect'}).get('result', {})
    R.until(lambda: not st().get('viewer', {}).get('placeWaiting', True), 30)
    if wins:
        R.x('xdotool', 'windowactivate', '--sync', wins[0][0])
        time.sleep(0.5)
        R.x('xdotool', 'key', 'Return')
    placed = R.until(lambda: (st().get('selectedEdit') or {}).get('kind') == 'cover', 20)
    s = st()
    R.facts['placed'] = {'selectedEdit': s.get('selectedEdit'), 'blurGuidance': s.get('blurGuidance'), 'panel': s.get('panel', {}).get('mode')}
    R.say('placed', json.dumps(R.facts['placed']))
    R.park()
    R.frame('blur-selected-wide', settle=1.5)
    R.say('resize', json.dumps(R.cli('recording.review', {'id': rid, 'action': 'resize', 'width': 1440, 'height': 700}))[:200])
    time.sleep(1.0)
    sel = (R.facts['placed'] or {}).get('selectedEdit') or {}
    R.cli('recording.review', {'id': rid, 'action': 'selectEdit', 'kind': 'trim'})
    R.say('reselect', json.dumps(R.cli('recording.review', {'id': rid, 'action': 'selectEdit', 'kind': 'cover', 'editId': sel.get('id')}))[:160])
    time.sleep(1.0)
    s = st()
    R.facts['folded'] = {'folded': s.get('folded'), 'blurGuidance': s.get('blurGuidance')}
    R.say('folded', json.dumps(R.facts['folded']))
    R.park()
    R.frame('blur-selected-folded', settle=1.5)
finally:
    if rid:
        R.say('cancel', json.dumps(R.cli('recording.cancel', {'id': rid}))[:200])
    R.cleanup()
