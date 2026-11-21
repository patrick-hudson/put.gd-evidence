#!/usr/bin/env python3
"""#1792 lab runner (from #1782): a headless private put.gd resident with a session-only B2 profile.

  run.py BUILD launch                       start the resident from ~/work/b1782/BUILD/usr/bin
  run.py BUILD configure [settings-json]    B2 profile (session credentials) into the isolated prefix
  run.py BUILD upload LABEL COUNT MIB       serial uploads, each checked in the bucket
          env CANCEL_AFTER=s cancels each upload after s seconds
  run.py BUILD identity                     build identity from diagnostics
  run.py BUILD stop                         quit the resident
No desktop session, no keychain: the key lives only in the resident's memory.
"""
import hashlib, json, os, pathlib, subprocess, sys, threading, time
from datetime import datetime, timezone

H = pathlib.Path(__file__).resolve().parent
build, action = sys.argv[1], sys.argv[2]
PKG = pathlib.Path.home() / 'work/b1792' / build
BIN = PKG / 'usr/bin'
state = json.loads((H / 'state.json').read_text())
RT = pathlib.Path(state['runtime']) / build
HOME = H / 'home' / build
TERMINAL = {'completed', 'failed', 'partial', 'cancelled', 'interrupted'}


def env():
    e = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'USER', 'LANG', 'LOGNAME')}
    e.update(XDG_RUNTIME_DIR=str(RT), XDG_CONFIG_HOME=str(HOME / 'config'), XDG_DATA_HOME=str(HOME / 'data'),
             XDG_CACHE_HOME=str(HOME / 'cache'), QT_QPA_PLATFORM='offscreen',
             LD_LIBRARY_PATH=str(PKG / 'usr/lib/x86_64-linux-gnu/putgd'), PATH=str(BIN) + ':' + os.environ['PATH'])
    return e


def cli(method, params=None, timeout=45):
    run = subprocess.run([str(BIN / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}),
                         text=True, capture_output=True, timeout=timeout, env=env())
    value = json.loads(run.stdout or '{}')
    if run.returncode or not value.get('ok'):
        raise RuntimeError(json.dumps({'cli': method, 'error': (value.get('error') or {}).get('code'), 'message': (value.get('error') or {}).get('message')}))
    return value['result']


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


if action == 'launch':
    for p in (RT, HOME / 'config', HOME / 'data', HOME / 'cache', HOME / 'archive'):
        p.mkdir(mode=0o700, parents=True, exist_ok=True)
    sock = RT / 'putgd/session.sock'
    assert len(os.fsencode(sock)) <= 107, len(os.fsencode(sock))
    log = open(H / f'resident-{build}.log', 'ab')
    proc = subprocess.Popen([str(BIN / 'putgd-launcher'), '--background'], stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                            start_new_session=True, env=env())
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not sock.is_socket():
        time.sleep(.1)
    if not sock.is_socket(): sys.exit('no resident socket')
    for _ in range(60):
        try:
            print(json.dumps({'socketBytes': len(os.fsencode(sock)), 'build': cli('ui.snapshot').get('build')}))
            break
        except RuntimeError as exc:
            if 'initializing' not in str(exc): raise
            time.sleep(1)
elif action == 'identity':
    d = cli('ui.snapshot')
    print(json.dumps({'build': d.get('diagnostics', {}).get('build', d.get('build')), 'qt': d.get('diagnostics', {}).get('qtVersion')}))
elif action == 'configure':
    settings = {'apiUrl': 'https://api.backblazeb2.com', 'bucket': state['bucketName'], 'objectPrefix': state['prefix'],
                'linkMode': 'public' if state['bucketType'] == 'allPublic' else 'authorized', 'linkValidityDays': 1,
                'publicUrlBase': None, 'connectTimeoutMs': 10000, 'requestTimeoutMs': 600000}
    if len(sys.argv) > 3: settings.update(json.loads(sys.argv[3]))
    profile = {'id': 'b2-live', 'label': 'Isolated B2', 'provider': 'backblaze-b2', 'settings': settings,
               'credentials': {'mode': 'session', 'reference': None}}
    current = cli('settings.get')
    output = {'destination': 'upload', 'profileId': 'b2-live', 'publicationMode': 'share'}
    cli('settings.patch', {'patch': {'profiles': [profile], 'captureDefaults': output, 'limits': {'concurrentUploads': int(os.environ.get('SLOTS', '4'))},
        'archive': {'keepUploads': True, 'root': str(HOME / 'archive')},
        'naming': {'mode': 'original', 'captureTemplate': 'cap-{uuid}.{ext}'},
        'preferences': {'notifications': False, 'fileManagerMenu': False, 'launchAtLogin': False, 'updates': {'check': False},
                        'unlockCredentialsAtStartup': False}}, 'expectedRevision': current['metadata']['observedRevision']})
    got = cli('settings.get')
    run = subprocess.run([sys.executable, str(H / 'b2acc.py'), 'key-to-cli', 'b2-live', got['metadata']['acceptedRevision'], str(RT / 'putgd/session.sock')],
                         capture_output=True, text=True, timeout=90, env=env())
    stored = json.loads(run.stdout.strip().splitlines()[-1]) if run.stdout.strip() else {'error': run.stderr[-200:]}
    if stored.get('setupId'):
        for _ in range(100):
            job = cli('setup.inspect', {'id': stored['setupId']})
            if job['state'] != 'running': stored['state'] = job['state']; stored['jobError'] = (job.get('error') or {}).get('code'); break
            time.sleep(.2)
    print(json.dumps({'requestTimeoutMs': settings['requestTimeoutMs'], 'linkMode': settings['linkMode'], 'stored': stored}))
elif action == 'upload':
    label, count, mib = sys.argv[3], int(sys.argv[4]), float(sys.argv[5])
    cancel_after = float(os.environ.get('CANCEL_AFTER', '0'))
    out = H / 'results'; out.mkdir(exist_ok=True)
    for index in range(1, count + 1):
        name = f'r1792-{build}-{label}-{index}.bin'
        path = H / 'files' / name; path.parent.mkdir(exist_ok=True)
        path.write_bytes(os.urandom(int(mib * 1024 * 1024)))
        started = stamp(); since = time.monotonic()
        lanes = {'max': 0, 'samples': [], 'stop': False}
        def sample():
            # Worker TCP connections to port 443 whose bytes_sent grew since the last sample.
            last = {}
            while not lanes['stop']:
                out = subprocess.run(['ss', '-tinpH', 'state', 'established', '( dport = :443 )'], capture_output=True, text=True).stdout.splitlines()
                active, now = 0, {}
                for i, line in enumerate(out):
                    if 'putgd-b2-worker' not in line or i + 1 >= len(out): continue
                    peer = line.split()[3] if len(line.split()) > 3 else line
                    m = __import__('re').search(r'bytes_sent:(\d+)', out[i + 1])
                    if not m: continue
                    now[peer] = int(m.group(1))
                    if now[peer] - last.get(peer, now[peer]) > 64 * 1024: active += 1
                last = now
                lanes['max'] = max(lanes['max'], active)
                lanes['samples'].append(active)
                time.sleep(1)
        sampler = threading.Thread(target=sample, daemon=True); sampler.start()
        accepted = cli('upload.files', {'paths': [str(path)], 'profileId': 'b2-live'})
        effect, cancelled, last = None, None, None
        changed, maxgap, lastsent = time.monotonic(), 0.0, None
        progress = []
        while time.monotonic() - since < 3 * 3600:
            if cancel_after and cancelled is None and time.monotonic() - since >= cancel_after:
                cli('operation.cancel', {'id': accepted['operationId']}); cancelled = round(time.monotonic() - since, 2)
            effect = cli('operation.inspect', {'id': accepted['operationId']})
            item = (effect.get('items') or [{}])[0]
            sent = (item.get('progress') or {}).get('bytesTransferred')
            if sent is not None and sent != lastsent:
                maxgap = max(maxgap, time.monotonic() - changed); changed, lastsent = time.monotonic(), sent
            if sent is not None and (not progress or time.monotonic() - progress[-1][0] - since >= 30):
                progress.append((round(time.monotonic() - since, 1), sent))
            if effect['state'] in TERMINAL: break
            time.sleep(1)
        elapsed = round(time.monotonic() - since, 2)
        lanes['stop'] = True; sampler.join(5)
        busy = [n for n in lanes['samples'] if n]
        item = (effect.get('items') or [{}])[0]
        error = item.get('error') or {}
        check = subprocess.run([sys.executable, str(H / 'b2acc.py'), 'check', name, str(path)], capture_output=True, text=True, timeout=120)
        bucket = json.loads(check.stdout) if check.returncode == 0 else {'checkError': (check.stdout + check.stderr)[-200:]}
        record = {'build': build, 'label': label, 'index': index, 'mib': mib, 'start': started, 'secondsToTerminal': elapsed,
                  'cancelledAt': cancelled, 'operationId': accepted['operationId'], 'state': effect.get('state'),
                  'uploadStatus': item.get('uploadStatus'), 'errorCode': error.get('code'), 'errorMessage': error.get('message'),
                  'errorDetails': error.get('details'), 'progress': progress, 'maxProgressGapSeconds': round(maxgap, 1), 'bucket': bucket,
                  'mibPerSecond': round(mib / elapsed, 3) if elapsed else None, 'maxSendingConnections': lanes['max'],
                  'sendingConnectionHistogram': {str(k): lanes['samples'].count(k) for k in sorted(set(lanes['samples']))}}
        with (out / f'{build}-{label}.jsonl').open('a') as f: f.write(json.dumps(record) + '\n')
        print(json.dumps({k: record[k] for k in ('index', 'secondsToTerminal', 'mibPerSecond', 'maxSendingConnections', 'sendingConnectionHistogram', 'state', 'uploadStatus', 'errorCode', 'errorMessage', 'bucket')}), flush=True)
        if not os.environ.get("KEEP"): path.unlink()
elif action == 'stop':
    try:
        for op in cli('operation.recent')['operations']:
            if op['state'] not in TERMINAL: cli('operation.cancel', {'id': op['id']})
        cli('ui.quit')
    except RuntimeError as exc:
        print(exc)
    print(json.dumps({'stopRequested': True}))
