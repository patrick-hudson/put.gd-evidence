#!/usr/bin/env python3
"""vmdrive.py RUN COMMAND [ARGS]: drive a #1363 lab guest from its QEMU host through tools/lab/lab.py.

  local                      enable a local-only output (Keep a local copy)
  cli METHOD [JSON]          one session method
  invoke ACTION [DELAY]      action.invoke and wait for the operation to end; prints action, state, error and image size
  move HEAD X Y              pointer to pixel X,Y of head HEAD (QMP tablet of that head)
  click HEAD X Y [right]     press and release there
  drag HEAD X1 Y1 X2 Y2      left drag within one head
  shot HEAD PATH             QMP screendump of a head as PNG
"""
import json, os, subprocess, sys, time
ROOT = os.path.expanduser('~/work/i1363')
LAB = [sys.executable, os.path.join(ROOT, 'tools/lab/lab.py')]
run = sys.argv[1]; RUN = os.path.join(ROOT, 'work/lab-runs', run)
state = json.load(open(os.path.join(RUN, 'state.json')))
def lab(*args, timeout=60):
    out = subprocess.run(LAB + list(args), capture_output=True, text=True, timeout=timeout)
    text = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr.strip()[-400:]
    try: return json.loads(text)
    except Exception: return {'ok': False, 'raw': text}
def cli(method, params=None):
    r = lab('cli', '--run', RUN, '--method', method, '--params', json.dumps(params or {}))
    return r.get('result', r) if isinstance(r, dict) and 'result' in r and 'ok' not in r else r
def sizes():
    layout = state.get('head_layout') or '1280x800+0+0'
    return [tuple(int(v) for v in part.split('+')[0].split('x')) for part in layout.split(',')]
def events(head, evs):
    # A tablet asked for the position it last reported sends nothing; with one tablet per
    # head the pointer then stays on the other head. Nudge before every absolute move.
    if evs and evs[0].get('type') == 'abs':
        lab('input', '--run', RUN, '--head', str(head), json.dumps([dict(e, data=dict(e['data'], value=max(e['data']['value'] - 60, 0))) for e in evs if e.get('type') == 'abs']))
    return lab('input', '--run', RUN, '--head', str(head), json.dumps(evs))
def absolute(head, x, y):
    w, h = sizes()[head]
    return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (w - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (h - 1))}}]
def extent():
    layout = state.get('head_layout') or '1280x800+0+0'; w = h = 0
    for part in layout.split(','):
        size, x, y = part.replace('-', '+-').split('+')[0], *[int(v) for v in part.replace('-', '+-').split('+')[1:3]]
        pw, ph = (int(v) for v in size.split('x')); w = max(w, x + pw); h = max(h, y + ph)
    return w, h
def gevents(evs):
    # The unbound tablet: Mutter and KWin scale it over the whole desktop.
    return lab('input', '--run', RUN, json.dumps(evs))
def gabsolute(x, y):
    w, h = extent()
    return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (w - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (h - 1))}}]
def gdrag(x1, y1, x2, y2):
    gevents(gabsolute(x1, y1)); time.sleep(0.3); gevents([button('left', True)]); time.sleep(0.2)
    for step in range(1, 9):
        gevents(gabsolute(x1 + (x2 - x1) * step // 8, y1 + (y2 - y1) * step // 8)); time.sleep(0.05)
    time.sleep(0.2); return gevents([button('left', False)])
def button(name, down):
    return {'type': 'btn', 'data': {'down': down, 'button': name}}
cmd = sys.argv[2]; a = sys.argv[3:]
if cmd == 'local':
    got = cli('settings.get'); res = got.get('result', got)
    print(json.dumps(cli('settings.patch', {'patch': {'archive': {'keepUploads': True}}, 'expectedRevision': res['metadata']['observedRevision']}))[:160])
elif cmd == 'cli':
    print(json.dumps(cli(a[0], json.loads(a[1]) if len(a) > 1 else {}))[:3000])
elif cmd == 'invoke':
    params = {'action': a[0]}
    if len(a) > 1 and a[1] != '0': params['delaySeconds'] = int(a[1])
    start = time.time(); r = cli('action.invoke', params); res = r.get('result', r)
    if 'operationId' not in res: print(json.dumps(r)[:500]); sys.exit(1)
    op = res['operationId']
    while time.time() - start < 90:
        o = cli('operation.inspect', {'id': op}); o = o.get('result', o)
        if o.get('state') not in ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording'):
            items = o.get('items', [])
            print(json.dumps({'id': op, 'action': o.get('action'), 'state': o.get('state'), 'error': o.get('error', {}).get('code'), 'message': o.get('error', {}).get('message'),
                              'seconds': round(time.time() - start, 1), 'local': [i.get('local', {}).get('path') for i in items]}))
            sys.exit(0)
        time.sleep(0.3)
    print('timeout', op); sys.exit(2)
elif cmd == 'region':
    # region HEAD X1 Y1 X2 Y2 [DELAY]: invoke, drag once the selector is up, wait for the result.
    head = int(a[0]); x1, y1, x2, y2 = (int(v) for v in a[1:5]); params = {'action': 'region'}
    if len(a) > 5 and a[5] != '0': params['delaySeconds'] = int(a[5])
    start = time.time(); r = cli('action.invoke', params); res = r.get('result', r); op = res.get('operationId')
    if not op: print(json.dumps(r)[:500]); sys.exit(1)
    time.sleep(2.0)
    events(head, absolute(head, x1, y1)); time.sleep(0.3); events(head, [button('left', True)]); time.sleep(0.2)
    for step in range(1, 9):
        events(head, absolute(head, x1 + (x2 - x1) * step // 8, y1 + (y2 - y1) * step // 8)); time.sleep(0.05)
    time.sleep(0.2); events(head, [button('left', False)]); released = time.time()
    while time.time() - start < 90:
        o = cli('operation.inspect', {'id': op}); o = o.get('result', o)
        if o.get('state') not in ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording'):
            print(json.dumps({'action': o.get('action'), 'state': o.get('state'), 'error': o.get('error', {}).get('code'), 'afterRelease': round(time.time() - released, 1),
                              'local': [i.get('local', {}).get('path') for i in o.get('items', [])]}))
            sys.exit(0)
        time.sleep(0.3)
    print('timeout', op); sys.exit(2)
elif cmd == 'start':
    # start ACTION DELAY: invoke and print the operation ID without waiting.
    params = {'action': a[0]}
    if len(a) > 1 and a[1] != '0': params['delaySeconds'] = int(a[1])
    r = cli('action.invoke', params); print(r.get('result', r).get('operationId', json.dumps(r)[:300]))
elif cmd == 'wait':
    start = time.time()
    while time.time() - start < 90:
        o = cli('operation.inspect', {'id': a[0]}); o = o.get('result', o)
        if o.get('state') not in ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording'):
            print(json.dumps({'action': o.get('action'), 'state': o.get('state'), 'error': o.get('error', {}).get('code'), 'message': o.get('error', {}).get('message'), 'items': len(o.get('items', []))}))
            sys.exit(0)
        time.sleep(0.3)
    print('timeout'); sys.exit(2)
elif cmd == 'gmove':
    print(json.dumps(gevents(gabsolute(int(a[0]), int(a[1]))))[:120])
elif cmd == 'gclick':
    name = a[2] if len(a) > 2 else 'left'
    gevents(gabsolute(int(a[0]), int(a[1]))); time.sleep(0.25); gevents([button(name, True)]); time.sleep(0.15); print(json.dumps(gevents([button(name, False)]))[:120])
elif cmd == 'gdrag':
    print(json.dumps(gdrag(*(int(v) for v in a[:4])))[:120])
elif cmd == 'gregion':
    # gregion X1 Y1 X2 Y2 [DELAY]: as region, in whole-layout coordinates.
    x1, y1, x2, y2 = (int(v) for v in a[:4]); params = {'action': 'region'}
    if len(a) > 4 and a[4] != '0': params['delaySeconds'] = int(a[4])
    start = time.time(); r = cli('action.invoke', params); res = r.get('result', r); op = res.get('operationId')
    if not op: print(json.dumps(r)[:500]); sys.exit(1)
    time.sleep(2.5); gdrag(x1, y1, x2, y2); released = time.time()
    while time.time() - start < 90:
        o = cli('operation.inspect', {'id': op}); o = o.get('result', o)
        if o.get('state') not in ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording'):
            print(json.dumps({'action': o.get('action'), 'state': o.get('state'), 'error': o.get('error', {}).get('code'), 'afterRelease': round(time.time() - released, 1)}))
            sys.exit(0)
        time.sleep(0.3)
    print('timeout', op); sys.exit(2)
elif cmd == 'move':
    print(json.dumps(events(int(a[0]), absolute(int(a[0]), int(a[1]), int(a[2]))))[:120])
elif cmd == 'click':
    head = int(a[0]); name = a[3] if len(a) > 3 else 'left'
    events(head, absolute(head, int(a[1]), int(a[2]))); time.sleep(0.25)
    events(head, [button(name, True)]); time.sleep(0.15); print(json.dumps(events(head, [button(name, False)]))[:120])
elif cmd == 'drag':
    head = int(a[0]); x1, y1, x2, y2 = (int(v) for v in a[1:5])
    events(head, absolute(head, x1, y1)); time.sleep(0.3); events(head, [button('left', True)]); time.sleep(0.2)
    for step in range(1, 9):
        events(head, absolute(head, x1 + (x2 - x1) * step // 8, y1 + (y2 - y1) * step // 8)); time.sleep(0.05)
    time.sleep(0.2); print(json.dumps(events(head, [button('left', False)]))[:120])
elif cmd == 'shot':
    r = lab('screenshot', '--run', RUN, '--head', a[0]); print(json.dumps(r)[:300])
elif cmd == 'wheel':
    # wheel HEAD X Y N: N wheel steps down (negative: up) with the pointer at X,Y of a head.
    head = int(a[0]); n = int(a[3]); events(head, absolute(head, int(a[1]), int(a[2]))); time.sleep(0.2)
    for _ in range(abs(n)):
        name = 'wheel-down' if n > 0 else 'wheel-up'
        events(head, [button(name, True)]); events(head, [button(name, False)]); time.sleep(0.05)
    print('wheel', n)
elif cmd == 'gwheel':
    n = int(a[2]); gevents(gabsolute(int(a[0]), int(a[1]))); time.sleep(0.2)
    for _ in range(abs(n)):
        name = 'wheel-down' if n > 0 else 'wheel-up'
        gevents([button(name, True)]); gevents([button(name, False)]); time.sleep(0.05)
    print('wheel', n)
elif cmd == 'patch':
    # patch JSON: settings.patch with the current revision.
    got = cli('settings.get'); res = got.get('result', got)
    print(json.dumps(cli('settings.patch', {'patch': json.loads(a[0]), 'expectedRevision': res['metadata']['observedRevision']}))[:120])
