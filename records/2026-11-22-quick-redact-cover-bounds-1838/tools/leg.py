"""#1838 acceptance leg, run on the desktop host against a running driver.py.
Usage: leg.py ROOT FIXTURE_DIR LABEL [--sensitive]
editor:    fixture fullscreen -> editor.open desktop -> redactText card,key,email ->
           frame of the editor -> saveCopy -> cancel.
sensitive: Look for card/key/email on, monitor capture with sensitiveText=prompt ->
           decide redact -> frame of the editor -> editor.submit -> received object.
Writes ROOT/out/LABEL-*.png and LABEL-leg.json. Synthetic test values only."""
import json
import socket
import sys
import time
from pathlib import Path


def call(root, *command):
    s = socket.socket(socket.AF_UNIX)
    s.connect(str(root / 'c.sock'))
    s.settimeout(900)
    s.sendall(json.dumps(list(command)).encode() + b'\n')
    data = b''
    while not data.endswith(b'\n'):
        chunk = s.recv(65536)
        if not chunk:
            break
        data += chunk
    reply = json.loads(data)
    if 'error' in reply:
        raise RuntimeError(f'{command[0]}: {reply["error"]}')
    return reply['result']


def cli(root, name, params=None):
    reply = call(root, 'cli', name, params or {})
    if not reply.get('ok'):
        raise RuntimeError(f'{name}: {reply.get("error")}')
    return reply['result']


def retry(root, name, params, codes=('editor_active', 'editor_starting'), seconds=30):
    limit = time.monotonic() + seconds
    while True:
        reply = call(root, 'cli', name, params)
        if reply.get('ok'):
            return reply['result']
        code = (reply.get('error') or {}).get('code')
        if code not in codes or time.monotonic() > limit:
            raise RuntimeError(f'{name}: {reply.get("error")}')
        time.sleep(.5)


def main():
    root, fixture, label = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    sensitive = '--sensitive' in sys.argv
    out = root / 'out'
    record = {'label': label}
    # The pointer rests on empty paper, clear of the viewer's check points.
    call(root, 'move', 1500, 950)
    call(root, 'show', str(fixture / 'fixture.png'), True, True)
    if not sensitive:
        op = cli(root, 'editor.open', {'source': 'desktop'})
        oid = op.get('operationId') or op.get('id')
        record['operation'] = oid
        result = retry(root, 'editor.apply', {'id': oid, 'commands': [{'op': 'redactText', 'categories': ['card', 'key', 'email']}]}, seconds=60)
        record['redactText'] = result
        time.sleep(1.0)
        record['frame'] = call(root, 'shot', f'{label}-editor')
        path = out / f'{label}-saved.png'
        retry(root, 'editor.saveCopy', {'id': oid, 'path': str(path), 'overwrite': True})
        record['inspect'] = cli(root, 'editor.inspect', {'id': oid})
        record['saved'] = str(path)
        cli(root, 'editor.cancel', {'id': oid})
    else:
        call(root, 'prefs', {'preferences': {'sensitiveTextCheck': {'enabled': True, 'categories': ['card', 'key', 'email']}}})
        record['check'] = cli(root, 'settings.get')['document']['preferences'].get('sensitiveTextCheck')
        oid = call(root, 'capture', label, 'monitor', 'prompt', None, [1500, 950])
        record['operation'] = oid
        found = call(root, 'observe', oid, 'sensitive_text_found', 120)
        record['found'] = found.get('sensitive')
        call(root, 'decide', oid, 'redact')
        record['view'] = retry(root, 'editor.inspect', {'id': oid}, codes=('editor_active', 'editor_starting', 'editor_not_found', 'operation_not_found'), seconds=60)
        # The suggested marks come once recognition is done.
        limit = time.monotonic() + 60
        while time.monotonic() < limit:
            view = cli(root, 'editor.inspect', {'id': oid})
            if any(shape.get('suggested') for shape in view.get('shapes', [])):
                break
            time.sleep(.5)
        record['view'] = view
        time.sleep(1.0)
        record['frame'] = call(root, 'shot', f'{label}-editor')
        cli(root, 'editor.submit', {'id': oid})
        record['end'] = call(root, 'observe', oid, 'end', 120)
        record['collected'] = call(root, 'collect', oid, label)
    call(root, 'show', '', False, False)
    (out / f'{label}-leg.json').write_text(json.dumps(record, indent=1))
    print(json.dumps({k: v for k, v in record.items() if k in ('operation', 'redactText', 'frame', 'saved', 'found', 'collected')}, indent=1))


main()
