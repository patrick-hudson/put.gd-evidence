#!/usr/bin/env python3
"""Annotate the #1361 pictures with put.gd's own image editor, through putgd-cli.

  python3 annotate1361.py --cli PATH --in DIR --out DIR --spec FILE

The resident is the one putgd-cli reaches through this process's XDG_* variables (a private,
headless one is enough). For each picture named in the spec: editor.open on the file,
editor.apply with its shapes, editor.saveCopy into --out, editor.cancel. Nothing is uploaded.
The spec is JSON: {"file.png": [shape, ...]} with the shapes of docs/design/image-editor.md
(rectangle, arrow, text).
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--cli', required=True)
parser.add_argument('--in', dest='source', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--spec', required=True)
options = parser.parse_args()


def cli(method, params):
    out = subprocess.run([options.cli, '--params-stdin', method], input=json.dumps(params), capture_output=True, text=True, timeout=120)
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:200]}, 'result': {}}


spec = json.loads(Path(options.spec).read_text())
Path(options.out).mkdir(parents=True, exist_ok=True)
failed = 0
for name, shapes in spec.items():
    # The editor of the picture before takes a moment to close after its cancel.
    waiting = time.monotonic() + 30
    while True:
        opened = cli('editor.open', {'source': 'file', 'path': str(Path(options.source) / name)})
        if opened['ok'] or opened['error'].get('code') not in ('editor_active', 'editor_finalizing') or time.monotonic() > waiting:
            break
        time.sleep(0.4)
    if not opened['ok']:
        print(name, 'open failed:', opened['error'].get('code'), opened['error'].get('message'))
        failed += 1
        continue
    editor = opened['result']['operationId']
    # An entry with its own "op" (a crop) is a command as written; anything else is a shape to add.
    commands = [entry if 'op' in entry else {'op': 'add', 'shape': entry} for entry in shapes]
    deadline = time.monotonic() + 30
    while True:
        applied = cli('editor.apply', {'id': editor, 'commands': commands}) if commands else {'ok': True}
        if applied['ok'] or applied['error'].get('code') != 'editor_starting' or time.monotonic() > deadline:
            break
        time.sleep(0.3)
    saved = cli('editor.saveCopy', {'id': editor, 'path': str(Path(options.out) / name), 'overwrite': True}) if applied['ok'] else applied
    cli('editor.cancel', {'id': editor})
    print(name, 'ok' if saved['ok'] else 'FAILED %s: %s' % (saved['error'].get('code'), saved['error'].get('message')))
    failed += 0 if saved['ok'] else 1
sys.exit(1 if failed else 0)
