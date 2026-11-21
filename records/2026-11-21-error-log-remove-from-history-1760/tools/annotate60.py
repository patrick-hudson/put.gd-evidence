#!/usr/bin/env python3
"""Annotate a frame with put.gd's own editor (editor.open/apply/saveCopy/cancel) on the acc60 resident.
  annotate60.py SPEC.json   SPEC: {"input", "output", "crop": [x,y,w,h], "shapes": [...]}"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import acc60


def retry(method, params, busy=('editor_starting', 'editor_active'), tries=120):
    for _ in range(tries):
        reply = acc60.call(method, params)
        if reply['ok'] or reply['error']['code'] not in busy:
            return reply
        time.sleep(.25)
    return reply


spec = json.loads(Path(sys.argv[1]).read_text())
opened = retry('editor.open', {'source': 'file', 'path': spec['input']})
if not opened['ok']:
    raise SystemExit(json.dumps(opened))
op = opened['result']['operationId']
commands = [{'op': 'add', 'shape': shape} for shape in spec['shapes']] + [{'op': 'crop', 'rect': spec['crop']}]
applied = retry('editor.apply', {'id': op, 'commands': commands})
if not applied['ok']:
    raise SystemExit(json.dumps(applied))
saved = retry('editor.saveCopy', {'id': op, 'path': spec['output'], 'overwrite': True})
acc60.call('editor.cancel', {'id': op})
print(json.dumps({'saved': saved['ok'], 'error': saved['error'], 'output': spec['output']}))
