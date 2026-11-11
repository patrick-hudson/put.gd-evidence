#!/usr/bin/env python3
"""FIX-5 loop driver (PR #1398): cancel/quit/kill races against the GNOME Shell extension's bar placement.

Run on f44 from SSH, holding the desktop lock.
  fx5.py RUN VARIANT COUNT [--delays 0,0.05,...] [--recover]
RUN is a short directory name under ~/work/fx5 (private XDG dirs live there).
Variants (scroll):  pcq  prepare, cancel at once, ui.quit
                    pc   prepare, cancel, no quit
                    pk   prepare, kill the helper (SIGKILL by pid)
                    sc   prepare, start, cancel within 100 ms
                    sq   prepare, start, ui.quit mid-capture
Variants (recording): rpcq rpc rpk rsc rsq, the same with recording.* on a region.
Each iteration writes one JSON line to RUN/loop.jsonl; a changed gnome-shell pid is a crash.
"""
import argparse, json, os, signal, subprocess, sys, time
from pathlib import Path

BASE = Path.home() / 'work/fx5'
REAL = '/run/user/%d' % os.getuid()
RECT = [100, 200, 960, 600]
BIN = os.environ.get('FX5_BIN', '/usr/bin')


def real_env():
    return dict(os.environ, XDG_RUNTIME_DIR=REAL, DBUS_SESSION_BUS_ADDRESS='unix:path=%s/bus' % REAL)


def shell_pid():
    out = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'gnome-shell'], capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else 0


class Run:
    def __init__(self, name):
        self.dir = BASE / name
        self.dir.mkdir(exist_ok=True)
        for n in ('c', 'd', 's', 'cache', 'r', 'archive'):
            (self.dir / n).mkdir(mode=0o700, exist_ok=True)
        self.sock = self.dir / 'r/putgd/session.sock'
        assert len(str(self.sock).encode()) <= 107
        self.env = {'HOME': os.environ['HOME'], 'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'en_US.UTF-8',
                    'USER': os.environ.get('USER', ''), 'XDG_RUNTIME_DIR': str(self.dir / 'r'),
                    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=%s/bus' % REAL, 'XDG_SESSION_TYPE': 'wayland',
                    'XDG_CURRENT_DESKTOP': 'GNOME', 'XDG_SESSION_DESKTOP': 'gnome', 'DESKTOP_SESSION': 'gnome',
                    'WAYLAND_DISPLAY': REAL + '/wayland-0', 'QT_QPA_PLATFORM': 'wayland',
                    'XDG_CONFIG_HOME': str(self.dir / 'c'), 'XDG_DATA_HOME': str(self.dir / 'd'),
                    'XDG_STATE_HOME': str(self.dir / 's'), 'XDG_CACHE_HOME': str(self.dir / 'cache'),
                    'PIPEWIRE_RUNTIME_DIR': REAL, 'PULSE_SERVER': 'unix:%s/pulse/native' % REAL,
                    'PUTGD_RECORD_DEBUG_LOG': str(self.dir / 'helper.log'), 'SC_Y': '200'}
        self.resident = None
        self.fixture = None
        self.configured = (self.dir / 'configured').exists()

    def rpc(self, method, params=None, check=True, timeout=70):
        t0 = time.time()
        r = subprocess.run([BIN + '/putgd-cli', '--socket', str(self.sock), method, json.dumps(params or {})],
                           env=self.env, text=True, capture_output=True, timeout=timeout)
        try:
            o = json.loads(r.stdout)
        except ValueError:
            o = {'ok': False, 'raw': r.stdout[-300:], 'stderr': r.stderr[-300:], 'rc': r.returncode}
        with open(self.dir / 'rpc.jsonl', 'a') as f:
            f.write(json.dumps({'t0': t0, 't1': time.time(), 'method': method, 'params': params or {}, 'reply': o}) + '\n')
        if check and not o.get('ok'):
            raise RuntimeError('%s: %s' % (method, json.dumps(o)[:400]))
        return o.get('result', o) if o.get('ok') else o

    def owned(self, prefix='putgd'):
        mark = ('XDG_CONFIG_HOME=' + str(self.dir / 'c')).encode()
        found = []
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit():
                continue
            try:
                comm = (proc / 'comm').read_text().strip()
                if comm.startswith(prefix) and mark in (proc / 'environ').read_bytes().split(b'\0'):
                    stat = (proc / 'stat').read_text()
                    found.append({'pid': int(proc.name), 'comm': comm, 'ppid': int(stat[stat.rindex(')') + 2:].split()[1])})
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
        return found

    def start_resident(self):
        if self.resident and self.resident.poll() is None:
            return
        for stale in (self.sock,):
            if stale.exists() and not self.owned():
                stale.unlink()
        self.resident = subprocess.Popen([BIN + '/putgd', '--background'], env=self.env,
                                         stdout=open(self.dir / 'resident.log', 'a'), stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(150):
            if self.sock.exists():
                try:
                    self.rpc('settings.get', timeout=10)
                    break
                except Exception:
                    pass
            time.sleep(0.1)
        else:
            raise RuntimeError('resident did not start')
        if not self.configured:
            s = self.rpc('settings.get')
            d = s['document']
            d['preferences']['notifications'] = False
            d['archive'].update(keepUploads=True, root=str(self.dir / 'archive'))
            self.rpc('settings.save', {'document': d, 'expectedRevision': s['metadata']['observedRevision']})
            (self.dir / 'configured').write_text('1')
            self.configured = True
            time.sleep(2)
        self.close_ui()

    def close_ui(self):
        for p in self.owned('putgd-ui'):
            try:
                os.kill(p['pid'], signal.SIGTERM)
            except ProcessLookupError:
                pass

    def stop_resident(self, quit_first=True):
        if quit_first and self.sock.exists():
            try:
                self.rpc('ui.quit', check=False, timeout=15)
            except Exception:
                pass
        if self.resident:
            try:
                self.resident.wait(10)
            except subprocess.TimeoutExpired:
                pass
        time.sleep(0.3)
        for p in self.owned():
            try:
                os.kill(p['pid'], signal.SIGTERM)
            except ProcessLookupError:
                pass
        self.resident = None

    def wait_resident_exit(self, seconds=10):
        if self.resident:
            try:
                self.resident.wait(seconds)
            except subprocess.TimeoutExpired:
                return False
        self.resident = None
        return True

    def start_fixture(self, start=0):
        if self.fixture and self.fixture.poll() is None:
            return
        self.fixture = subprocess.Popen(['python3', str(BASE / 'qt_fixture.py'), '--rows', '600', '--start', str(start)], env=self.env,
                                        stdout=open(self.dir / 'fixture.log', 'a'), stderr=subprocess.STDOUT, start_new_session=True)
        time.sleep(3)

    def stop_fixture(self):
        if self.fixture and self.fixture.poll() is None:
            self.fixture.terminate()
            try:
                self.fixture.wait(10)
            except subprocess.TimeoutExpired:
                self.fixture.kill()
        self.fixture = None

    def helper_pids(self):
        return [p['pid'] for p in self.owned('putgd-record')]


def wait_state(run, kind, ident, wanted, seconds=20):
    v = {}
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        v = run.rpc(kind + '.inspect', {'id': ident}, check=False)
        if v.get('state') in wanted:
            return v
        time.sleep(0.05)
    return v


def probe(run, variant):
    kind = 'recording' if variant.startswith('r') else 'scroll'
    run.start_resident()
    t0 = time.monotonic()
    if kind == 'recording':
        v = run.rpc('recording.prepare', {'target': {'kind': 'region', 'rect': RECT}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}}, check=False)
    else:
        v = run.rpc('scroll.prepare', {'rect': RECT}, check=False)
    t1 = time.monotonic()
    ident = v.get('recordingId') or v.get('id')
    w = wait_state(run, kind, ident, ('ready', 'failed', 'cancelled')) if ident else {}
    t2 = time.monotonic()
    time.sleep(1.5)
    c = run.rpc(kind + '.cancel', {'id': ident}, check=False) if ident else {}
    time.sleep(1.5)
    return {'probe': kind, 'prepare': v.get('state', v), 'prepareS': round(t1 - t0, 3), 'readyS': round(t2 - t0, 3), 'ready': w.get('state'),
            'overlay': {k: w.get(k) for k in ('overlayPlacement', 'overlayExcluded')}, 'cancel': c.get('state', c)}


def iteration(run, variant, delay):
    rec = variant.startswith('r')
    kind = 'recording' if rec else 'scroll'
    step = variant[1:] if rec else variant
    out = {'variant': variant, 'delay': delay, 't': time.time()}
    run.start_resident()
    if step in ('sc', 'sq'):
        run.start_fixture(12000)
    if rec:
        v = run.rpc('recording.prepare', {'target': {'kind': 'region', 'rect': RECT}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}}, check=False)
    else:
        v = run.rpc('scroll.prepare', {'rect': RECT}, check=False)
    for _ in range(40):
        # A resident restarted after a quit mid-capture first recovers its journal.
        if (v.get('error') or {}).get('code') != 'initializing':
            break
        time.sleep(0.5)
        v = run.rpc(kind + '.prepare', {'target': {'kind': 'region', 'rect': RECT}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}} if rec else {'rect': RECT}, check=False)
    ident = v.get('recordingId') or v.get('id') or v.get('operationId')
    out['preparedAt'] = time.time()
    out['prepare'] = v.get('state', v)
    out['id'] = ident
    if not ident:
        out['fatal'] = True
        return out
    if step in ('sc', 'sq'):
        v = wait_state(run, kind, ident, ('ready', 'failed', 'cancelled'))
        out['ready'] = v.get('state')
        if rec:
            time.sleep(0.3)
        s = run.rpc(kind + '.start', {'id': ident}, check=False)
        out['start'] = s.get('state', s)
        if step == 'sq' and rec:
            time.sleep(1.0)
    elif rec:
        # recording.prepare answers "preparing"; the race is the same either way, so cancel on the same clock.
        pass
    if delay:
        time.sleep(delay)
    if step == 'pk':
        pids = run.helper_pids()
        out['killed'] = pids
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.5)
        v = run.rpc(kind + '.inspect', {'id': ident}, check=False)
        out['after'] = v.get('state', v)
        if v.get('state') not in ('failed', 'cancelled', 'done', 'finished'):
            c = run.rpc(kind + '.cancel', {'id': ident}, check=False)
            out['cancel'] = c.get('state', c)
    elif step in ('pcq', 'pc', 'sc'):
        c = run.rpc(kind + '.cancel', {'id': ident}, check=False)
        out['cancel'] = c.get('state', c)
        if step == 'pcq':
            q = run.rpc('ui.quit', check=False)
            out['quit'] = q.get('quitting', q)
            out['exited'] = run.wait_resident_exit()
            run.stop_resident(quit_first=False)
    elif step == 'sq':
        q = run.rpc('ui.quit', check=False)
        out['quit'] = q.get('quitting', q)
        out['exited'] = run.wait_resident_exit()
        run.stop_resident(quit_first=False)
    time.sleep(0.6)
    out['helpersLeft'] = run.helper_pids()
    return out


def recover(run, log):
    """After a Shell crash: bring the session back, leave the overview, restart the wall, check the extension."""
    for p in run.owned():
        try:
            os.kill(p['pid'], signal.SIGTERM)
        except ProcessLookupError:
            pass
    run.resident = None
    run.stop_fixture()
    time.sleep(8)
    info = {'shellAfterCrash': shell_pid()}
    # gnome-session turns every user extension off after a Shell crash.
    info['disableUserExtensions'] = subprocess.run(['gsettings', 'get', 'org.gnome.shell', 'disable-user-extensions'], env=real_env(), capture_output=True, text=True).stdout.strip()
    subprocess.run(['gsettings', 'set', 'org.gnome.shell', 'disable-user-extensions', 'false'], env=real_env())
    if not info['shellAfterCrash']:
        info['gdmRestart'] = subprocess.run(['sudo', '-n', 'systemctl', 'restart', 'gdm']).returncode
    for _ in range(40):
        if shell_pid():
            break
        time.sleep(1)
    time.sleep(8)
    env = real_env()
    subprocess.run(['gdbus', 'call', '--session', '-d', 'org.gnome.Shell', '-o', '/org/gnome/Shell', '-m',
                    'org.freedesktop.DBus.Properties.Set', 'org.gnome.Shell', 'OverviewActive', '<false>'], env=env, capture_output=True)
    subprocess.run(['systemctl', '--user', 'restart', 'putgd-gnome-vnc.service'], env=env)
    time.sleep(3)
    info['shell'] = shell_pid()
    info['extension'] = subprocess.run(['gnome-extensions', 'info', 'putgd@put.gd'], env=env, capture_output=True, text=True).stdout
    info['vt'] = Path('/sys/class/tty/tty0/active').read_text().strip()
    log(dict(recovered=info))
    return info['shell'] and 'ACTIVE' in info['extension']


def main():
    z = argparse.ArgumentParser()
    z.add_argument('run'); z.add_argument('variant'); z.add_argument('count', type=int)
    z.add_argument('--delays', default='0')
    z.add_argument('--recover', action='store_true')
    a = z.parse_args()
    run = Run(a.run)
    delays = [float(x) for x in a.delays.split(',')]

    def log(entry):
        with open(run.dir / 'loop.jsonl', 'a') as f:
            f.write(json.dumps(entry) + '\n')
        print(json.dumps(entry), flush=True)

    crashes = 0
    done = 0
    shell = shell_pid()
    log({'begin': a.variant, 'count': a.count, 'delays': delays, 'shell': shell, 'time': time.time(),
         'build': subprocess.run([BIN + '/putgd-cli', '--version-json'], capture_output=True, text=True).stdout.strip()})
    try:
        if a.variant.startswith('probe'):
            for i in range(a.count):
                log(probe(run, a.variant[5:] or 'p'))
            return
        for i in range(a.count):
            delay = delays[i % len(delays)]
            try:
                entry = iteration(run, a.variant, delay)
            except Exception as ex:
                entry = {'variant': a.variant, 'delay': delay, 'error': '%s: %s' % (type(ex).__name__, ex)}
            time.sleep(0.4)
            if entry.get('fatal'):
                # A refused prepare is how a dying Shell first shows: its pid stays listed while the core is written.
                time.sleep(4)
            now = shell_pid()
            entry.update(i=i, shellBefore=shell, shellAfter=now, crash=now != shell)
            if entry.get('fatal') and now != shell:
                entry['crashOf'] = i - 1
            log(entry)
            if entry.get('fatal') and now == shell:
                break
            if not entry.get('fatal'):
                done += 1
            if now != shell:
                crashes += 1
                if not a.recover or not recover(run, log):
                    break
                shell = shell_pid()
        # The extension may still be placing the last bar (up to ~3.5 s after the cancel).
        time.sleep(4)
        if shell_pid() != shell:
            crashes += 1
            log({'lateCrash': True, 'shellBefore': shell, 'shellAfter': shell_pid()})
            if a.recover:
                recover(run, log)
    finally:
        run.stop_fixture()
        run.stop_resident()
        log({'end': a.variant, 'iterations': done, 'crashes': crashes, 'left': run.owned(), 'shell': shell_pid(), 'time': time.time()})
    sys.exit(2 if crashes else 0)


if __name__ == '__main__':
    main()
