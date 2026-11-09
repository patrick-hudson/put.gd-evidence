#!/usr/bin/env python3
"""Issue #835 witness: drive a disposable lab guest and read what Qt delivered."""
import json
import shlex
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/lab')
import lab  # noqa: E402

PNG = r'''
import struct, zlib
w, h = 640, 400
raw = b''.join(b'\0' + bytes((x * 255 // w, y * 255 // h, 90)) * 1 + b''.join(bytes(((x + i) * 255 // w % 256, y * 255 // h, 90)) for i in range(1, w)) for y in range(h) for x in [0])
def chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
open('/home/lab/seed.png', 'wb').write(data)
'''


def session(run, body, timeout=60):
    return lab.guest_session(run, body, timeout=timeout)


def cli(run, method, params=None):
    reply = json.loads(session(run, 'putgd-cli ' + shlex.quote(method) + ' ' + shlex.quote(json.dumps(params or {})) + ' || true\n'))
    if not reply.get('ok'):
        raise RuntimeError(method + ': ' + json.dumps(reply.get('error')))
    return reply['result']


def wait(fn, label, timeout=45):
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        try:
            value = fn()
            if value:
                return value
        except Exception as error:  # the guest is mid-transition
            last = error
        time.sleep(1)
    raise SystemExit(f'timeout: {label}: {last}')


def prep(run, probe):
    lab.acceptance_preflight(run, apply=True, stage='start')
    # Never reuse a resident the probe is not loaded into.
    print(session(run, 'pgrep -a -x putgd || true\npgrep -a -x putgd-ui || true\n'))
    if probe:
        lab.put(run, 'work/keyprobe.so', '/home/lab/keyprobe.so')
    preload = 'export LD_PRELOAD=$HOME/keyprobe.so PUTGD_KEY_PROBE_DIR=$HOME/keyprobe\n' if probe else ''
    try:
        cli(run, 'ui.quit')
        time.sleep(3)
    except Exception as error:
        print('no resident to quit:', error)
    session(run, 'mkdir -p ~/putgd-lab ~/keyprobe\nfind ~/keyprobe -maxdepth 1 -name "keyprobe-*.log" -delete\n' + preload +
            'nohup putgd-launcher --background > ~/putgd-lab/app.log 2>&1 < /dev/null &\n')
    wait(lambda: cli(run, 'capabilities'), 'resident answers')
    current = cli(run, 'settings.get')
    print(json.dumps(cli(run, 'settings.patch', {'expectedRevision': current['metadata']['observedRevision'],
          'patch': {'actions': {'edit': {'destination': 'local', 'profileId': None}}, 'archive': {'keepUploads': True, 'root': '/home/lab/putgd-lab/archive'}}}))[:200])
    session(run, 'python3 - <<"PY"\n' + PNG + '\nPY\n')
    existing = cli(run, 'history.list', {'limit': 5}).get('records')
    if existing:
        print('history row exists:', existing[0]['id'])
        cli(run, 'ui.show', {'view': 'history'})
        time.sleep(3)
        return
    try:
        op = cli(run, 'editor.open', {'source': 'file', 'path': '/home/lab/seed.png'})['operationId']
    except RuntimeError as error:
        details = json.loads(str(error).split(': ', 1)[1])
        if details.get('code') != 'editor_active':
            raise
        op = details['details']['operationId']
    print(json.dumps(wait(lambda: cli(run, 'editor.inspect', {'id': op}), 'editor ready'))[:500])
    print(json.dumps(cli(run, 'editor.submit', {'id': op}))[:500])
    items = wait(lambda: cli(run, 'history.list', {'limit': 5}).get('records'), 'history row')
    print(json.dumps(items[0])[:400])
    cli(run, 'ui.show', {'view': 'history'})
    time.sleep(3)
    print(json.dumps(cli(run, 'ui.history', {'action': 'inspect'}))[:600])


def click(run, x, y, width, height, button='left'):
    lab.pointer(run, x, y, width, height)
    time.sleep(.2)
    lab.pointer(run, x, y, width, height, down=True, button=button)
    time.sleep(.1)
    lab.pointer(run, x, y, width, height, down=False, button=button)


def main():
    command, run = sys.argv[1], str(Path(sys.argv[2]).absolute())
    if command == 'prep':
        prep(run, len(sys.argv) < 4 or sys.argv[3] != 'noprobe')
    elif command == 'click':
        x, y, width, height = map(int, sys.argv[3:7])
        click(run, x, y, width, height)
    elif command == 'key':
        lab.key(run, sys.argv[3:])
    elif command == 'log':
        print(session(run, 'cat ~/keyprobe/keyprobe-*.log 2>/dev/null || true\n'))
    elif command == 'reset-log':
        session(run, 'for f in ~/keyprobe/keyprobe-*.log; do : > "$f"; done\n')
    elif command == 'cli':
        print(json.dumps(cli(run, sys.argv[3], json.loads(sys.argv[4]) if len(sys.argv) > 4 else {})))
    elif command == 'sh':
        print(session(run, sys.argv[3] + '\n', timeout=60))
    else:
        raise SystemExit('unknown command')


main()
