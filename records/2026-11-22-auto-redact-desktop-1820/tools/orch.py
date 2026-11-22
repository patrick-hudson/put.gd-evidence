"""Workstation-side orchestration of driver.py on a builder (pinned BatchMode SSH via bin/rs)."""
import json
import subprocess
import sys
import time
from pathlib import Path

S = Path(__file__).resolve().parent.parent
REPO = '/home/patrick/.t3/worktrees/put.gd/t3-05a5431b-1acc34bf3391252b'
ALL = ['card', 'key', 'list', 'email', 'phone', 'ip', 'name']


class Host:
    def __init__(self, host, session, fxdir, lock_host=None, results=None):
        self.host, self.session = host, session
        self.lock_host = lock_host
        self.root = (S / f'{host}.root').read_text().strip()
        self.fx = Path(fxdir)
        self.truth = json.loads((self.fx / 'truth.json').read_text())
        self.res = Path(results or S / 'results' / host)
        self.res.mkdir(parents=True, exist_ok=True)
        self.beat = time.time()
        self.log = (self.res / 'run.jsonl').open('a')

    def call(self, method, *args, timeout=600):
        self.heartbeat()
        cmd = json.dumps([method, *args])
        out = subprocess.run([str(S / 'bin/dc'), self.host, cmd], capture_output=True, text=True, timeout=timeout).stdout
        try:
            reply = json.loads(out)
        except ValueError:
            raise RuntimeError(f'{method}: bad reply {out[-400:]}')
        if 'error' in reply:
            raise RuntimeError(f'{method}: {reply["error"]}')
        return reply['result']

    def heartbeat(self, force=False):
        if self.lock_host and (force or time.time() - self.beat > 420):
            subprocess.run([sys.executable, str(S / 'locktool/desktop_lock.py'), 'heartbeat', self.lock_host, '--session', self.session],
                           cwd=REPO, capture_output=True, timeout=60)
            self.beat = time.time()

    def pull(self, names):
        got = []
        for n in names:
            dest = self.res / Path(n).name
            r = subprocess.run([str(S / 'bin/rcp'), self.host, f'{self.host}:{n}', str(dest)], capture_output=True, text=True)
            if r.returncode == 0:
                got.append(str(dest))
        return got

    def kinds(self, mapping, **prefs):
        return self.call('kinds', mapping, True, **prefs)

    def record(self, entry):
        self.log.write(json.dumps(entry) + '\n')
        self.log.flush()

    def check(self, fid, original, upload, cover, offset=(0, 0)):
        args = ['uv', 'run', '-q', '--with', 'numpy', '--with', 'scipy', '--with', 'pillow', 'python3', str(S / 'kit/check.py'),
                str(self.fx / 'truth.json'), fid, original, upload, '--cover', ','.join(cover), '--offset', str(offset[0]), str(offset[1]),
                '--fixture-png', str(self.fx / f'{fid}.png'), '--json', str(Path(upload).with_suffix('.check.json'))]
        out = subprocess.run(args, capture_output=True, text=True).stdout.strip()
        try:
            return json.loads(out.splitlines()[-1])
        except (ValueError, IndexError):
            return {'error': out[-500:]}

    def expected_counts(self, fid, cover):
        fx = next(f for f in self.truth['fixtures'] if f['id'] == fid)
        counts, seen = {}, set()
        for t in fx['tokens']:
            if t['kind'] not in cover:
                continue
            if t.get('group'):
                if t['group'] in seen:
                    continue
                seen.add(t['group'])
            counts[t['kind']] = counts.get(t['kind'], 0) + 1
        return counts

    def run_capture(self, label, fid, cover, mode='agent', action='monitor', decide=None, pointer=(1915, 700), region=None, show=True):
        """Show fixture, capture, settle (decide if it pauses), collect, check pixels."""
        if show:
            self.call('show', str(Path(self.root) / 'fx' / f'{fid}.png'))
        n0 = len(self.call('notifications'))
        oid = self.call('capture', label, action, mode, region, list(pointer) if pointer else None)
        op = self.call('observe', oid, 'sensitive_text_found', 120)
        paused = op.get('phase') == 'sensitive_text_found'
        entry = {'label': label, 'fixture': fid, 'cover': cover, 'mode': mode, 'action': action, 'id': oid, 'paused': paused,
                 'sensitiveAtPause': op.get('sensitive') if paused else None}
        if paused:
            if decide:
                entry['decide'] = decide
                if decide != 'none':
                    entry['decideReply'] = self.call('decide', oid, decide)
            else:
                entry['unexpectedPause'] = True
                entry['decideReply'] = self.call('decide', oid, 'cancel')
            if decide != 'none':
                op = self.call('observe', oid, 'end', 120)
        else:
            op = self.call('observe', oid, 'end', 120)
        entry['state'] = op.get('state')
        entry['sensitive'] = op.get('sensitive')
        col = self.call('collect', oid, label)
        entry['collect'] = {k: col[k] for k in ('state', 'items', 'sensitive')}
        time.sleep(1.5)
        notes = self.call('notifications', n0)
        entry['notifications'] = notes
        files = col['uploads'] + [x['to'] for x in col['local']] + [x['to'] for x in col['original']]
        local = self.pull(files + [f'{self.root}/out/{label}-op.json'])
        entry['files'] = [Path(p).name for p in local]
        up = next((p for p in local if '-upload0' in p), None)
        loc = next((p for p in local if '-local0' in p), None)
        if up and loc:
            import hashlib
            entry['localEqualsUpload'] = hashlib.sha256(open(up, 'rb').read()).digest() == hashlib.sha256(open(loc, 'rb').read()).digest()
        entry['originalSaved'] = (entry.get('sensitive') or {}).get('original')
        orig = next((p for p in local if '-original0' in p), None)
        if up and orig:
            entry['pixels'] = self.check(fid, orig, up, cover if entry['state'] == 'completed' else [], region[:2] if region else (0, 0))
        elif up:
            entry['pixels'] = self.check(fid, str(self.fx / f'{fid}.png'), up, cover, region[:2] if region else (0, 0)) | {'note': 'no original copy; compared with fixture'}
        entry['expectedCovered'] = self.expected_counts(fid, cover)
        self.record(entry)
        return entry


class VHost(Host):
    """A lab guest on d69 reached through g.py."""
    def __init__(self, name, run, session, fxdir, results=None):
        self.host, self.session, self.lock_host, self.run = name, session, None, run
        self.fx = Path(fxdir); self.truth = json.loads((self.fx / 'truth.json').read_text())
        self.res = Path(results or S / 'results' / name); self.res.mkdir(parents=True, exist_ok=True)
        self.beat = time.time(); self.log = (self.res / 'run.jsonl').open('a')
        self.root = self._g('root').strip()

    def _g(self, *args, timeout=900):
        cmd = 'cd ~/work/a21lab && python3 g.py ' + ' '.join(shlex_quote(a) for a in (self.run, *args))
        return subprocess.run([str(S / 'bin/rs'), 'd69', cmd], capture_output=True, text=True, timeout=timeout).stdout

    def call(self, method, *args, timeout=900):
        out = self._g('dc', json.dumps([method, *args]), timeout=timeout)
        try:
            reply = json.loads(out)
        except ValueError:
            raise RuntimeError(f'{method}: bad reply {out[-400:]}')
        if 'error' in reply:
            raise RuntimeError(f'{method}: {reply["error"]}')
        return reply['result']

    def pull(self, names):
        got = []
        for n in names:
            mid = '/home/patrick/work/a21lab/pull/' + Path(n).name
            self._g('get', n, mid)
            dest = self.res / Path(n).name
            if subprocess.run([str(S / 'bin/rcp'), 'd69', 'd69:' + mid, str(dest)], capture_output=True).returncode == 0:
                got.append(str(dest))
        return got


from shlex import quote as shlex_quote
