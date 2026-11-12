#!/usr/bin/env python3
"""Desktop acceptance of Proton uploads for one builder desktop (#1400).

Runs a put.gd build on the live desktop session with a PRIVATE profile folder (its own
config, data and state), pointed at the builder's Proton lab account and folder. It never
touches the lab profile in ~/putgd-lab/proton, and never prints or stores a share link.

  proton_accept.py --app ROOT --work NEW_DIR --host HOST --session LOCK_SESSION [--only NAME ...]

ROOT is an extracted package: it holds AppRun (AppImage) or usr/bin/putgd-launcher (.deb/.rpm).
It refuses to start unless LOCK_SESSION holds both the builder's desktop lock and its Proton
lock (desktop_lock.py must sit next to this script). Writes NEW_DIR/results.json,
NEW_DIR/summary.txt and keeps the app's log and local copies of captures under NEW_DIR.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import threading
import urllib.request

SESSION_PROCESSES = ('gnome-shell', 'plasmashell', 'cinnamon')
SESSION_VARIABLES = ('DISPLAY', 'XAUTHORITY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_SESSION_TYPE',
                     'XDG_CURRENT_DESKTOP', 'WAYLAND_DISPLAY', 'XDG_CONFIG_DIRS', 'XDG_DATA_DIRS',
                     'XDG_RUNTIME_DIR', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION')
LAB_CONFIG = Path.home() / 'putgd-lab/proton/config/putgd/config.json'
PROFILE_ID = 'proton-lab'
TERMINAL = ('completed', 'partial', 'failed', 'cancelled')


class Failure(RuntimeError):
    pass


def require_locks(host, session):
    """Both the desktop and the Proton session must be locked by this session, now."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('desktop_lock', Path(__file__).resolve().parent / 'desktop_lock.py')
    locks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(locks)
    for resource in ('desktop', 'proton'):
        state = locks.Desktop(Path.home() / 'putgd-lab/locks', host, resource=resource).status()
        holder = (state.get('lock') or {}).get('session')
        if state.get('state') != 'held' or holder != session:
            raise SystemExit(f'REFUSED: the {host} {resource} lock is {state.get("state")} (holder {holder}), not held by {session}')


def desktop_environment():
    for name in SESSION_PROCESSES:
        found = subprocess.run(['pgrep', '-u', str(os.getuid()), '-n', '-x', name], capture_output=True, text=True)
        if found.returncode == 0 and found.stdout.strip():
            raw = Path(f'/proc/{found.stdout.split()[0]}/environ').read_bytes()
            values = dict(entry.decode(errors='replace').partition('=')[::2] for entry in raw.split(b'\0') if entry)
            return name, {key: values[key] for key in SESSION_VARIABLES if values.get(key)}
    raise Failure('No GNOME, Plasma or Cinnamon session is running on this builder')


def helper_pids():
    """This user's running Proton helper processes."""
    found = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid == os.getuid() and (entry / 'comm').read_text().strip().startswith('putgd-proton-ru'):
                found.append(int(entry.name))
        except OSError:
            continue
    return sorted(found)


class App:
    def __init__(self, root, work):
        self.root, self.work = Path(root).resolve(), Path(work).resolve()
        self.launcher = self.root / ('AppRun' if (self.root / 'AppRun').is_file() else 'usr/bin/putgd-launcher')
        if not self.launcher.is_file():
            raise Failure(f'{self.root} holds neither AppRun nor usr/bin/putgd-launcher')
        self.desktop, session = desktop_environment()
        keep = ('HOME', 'USER', 'LOGNAME', 'PATH', 'LANG', 'LC_ALL', 'SHELL', 'TZ')
        self.environment = {name: os.environ[name] for name in keep if name in os.environ}
        self.environment.update(session)
        for name in ('config', 'data', 'state'):
            (self.work / 'profile' / name).mkdir(parents=True, mode=0o700)
        self.environment.update(XDG_CONFIG_HOME=str(self.work / 'profile/config'),
                                XDG_DATA_HOME=str(self.work / 'profile/data'),
                                XDG_STATE_HOME=str(self.work / 'profile/state'))
        self.cli_environment = dict(self.environment)
        if self.launcher.name == 'AppRun':  # the CLI has no AppRun route; give it the image's libraries
            library = f'{self.root}/usr/lib:{self.root}/usr/lib/putgd'
            self.cli_environment['LD_LIBRARY_PATH'] = library
            self.cli_environment['QT_PLUGIN_PATH'] = f'{self.root}/usr/plugins:{self.root}/usr/lib/qt6/plugins'
        runtime = Path(self.environment['XDG_RUNTIME_DIR']).resolve()
        socket = str(runtime / 'putgd/session.sock')
        size = len(socket.encode('utf-8'))
        if size > 107:
            raise Failure(f'Unix socket path exceeds 107 bytes: {size}')
        print(f'Socket preflight: {socket} = {size} UTF-8 bytes', flush=True)
        self.process = None
        self.entries = []

    def authorize_capture(self):
        """KWin offers its screenshot interface only to a program whose desktop entry names its exact
        path. An extracted package has none, so write one for this run and remove it afterwards."""
        if self.desktop != 'plasmashell' or self.launcher.name == 'AppRun':
            return
        text = (self.root / 'usr/share/applications/putgd.desktop').read_text()
        text = text.replace('Exec=/usr/bin/putgd', f'Exec={self.root}/usr/bin/putgd')
        for folder in (Path.home() / '.local/share/applications', self.work / 'profile/data/applications'):
            target = folder / 'putgd.desktop'
            if target.exists():
                raise Failure(f'{target} already exists; not replacing it')
            folder.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
            self.entries.append(target)
        subprocess.run(['kbuildsycoca6', '--noincremental'], env=self.environment, capture_output=True, timeout=60)

    def remove_entries(self):
        for target in self.entries:
            target.unlink(missing_ok=True)
        if self.entries:
            subprocess.run(['kbuildsycoca6', '--noincremental'], env=self.environment, capture_output=True, timeout=60)

    def call(self, method, params=None, timeout=130):
        """One CLI request: (result, error). error is {'code', 'message'} or None."""
        done = subprocess.run([str(self.root / 'usr/bin/putgd-cli'), method, json.dumps(params or {})],
                              env=self.cli_environment, capture_output=True, text=True, timeout=timeout)
        try:
            reply = json.loads(done.stdout)
        except ValueError:
            return None, {'code': 'no_json_reply', 'message': f'exit {done.returncode}'}
        if not reply.get('ok'):
            error = reply.get('error') or {}
            return None, {'code': error.get('code', 'failed'), 'message': error.get('message', '')}
        return reply.get('result'), None

    def need(self, method, params=None, timeout=130):
        result, error = self.call(method, params, timeout)
        if error:
            raise Failure(f'{method}: {error["code"]}: {error["message"]}')
        return result

    def start(self):
        _, error = self.call('capabilities', timeout=15)
        if error is None:
            raise Failure('Another put.gd already answers on this desktop session; quit it first')
        log = open(self.work / 'resident.log', 'x')
        self.process = subprocess.Popen([str(self.launcher), '--background'], env=self.environment,
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                        start_new_session=True)
        deadline = time.monotonic() + 60
        while self.call('capabilities', timeout=15)[1] is not None:
            if time.monotonic() > deadline:
                raise Failure('The resident did not answer within 60 s; see resident.log')
            time.sleep(1)
        time.sleep(6)  # uploads are refused as `initializing` until saved credentials are read

    def stop(self):
        self.call('ui.quit', timeout=15)
        if self.process is None:
            return
        try:
            self.process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(self.process.pid, signal.SIGTERM)


def configure(app):
    """Adds the lab account's destination to the private profile and routes captures to it with a link."""
    lab = json.loads(LAB_CONFIG.read_text())
    profile = next(item for item in lab['profiles'] if item['id'] == PROFILE_ID)
    if not profile['settings'].get('folderName', '').startswith('putgd-lab-'):
        raise Failure('The lab destination is not an isolated putgd-lab- folder')
    settings = app.need('settings.get')
    route = {'destination': 'upload', 'profileId': PROFILE_ID, 'publicationMode': 'share'}
    patch = {'profiles': settings['document']['profiles'] + [profile],
             'actions': {name: route for name in ('desktop', 'monitor', 'region', 'window', 'clipboard')},
             'captureDefaults': route,  # file uploads take their link setting from here
             'archive': {'keepUploads': True, 'root': str(app.work / 'local-copies')}}
    app.need('settings.patch', {'patch': patch, 'expectedRevision': settings['metadata']['observedRevision']})
    return profile['settings']['folderName']


def follow(app, operation, invoked, budget=180, cancel_after=None):
    """Polls one operation to its end. Times are seconds since the action was invoked."""
    seen, record, cancelled = {}, None, False
    deadline = time.monotonic() + budget
    while time.monotonic() < deadline:
        record, error = app.call('operation.inspect', {'id': operation}, timeout=20)
        now = round(time.monotonic() - invoked, 2)
        if error is None:
            for phase in {record.get('phase', '')} | {item.get('phase', '') for item in record.get('items', [])}:
                seen.setdefault(phase, now)
            if record.get('state') in TERMINAL:
                break
        if cancel_after is not None and not cancelled and now >= cancel_after:
            app.call('operation.cancel', {'id': operation}, timeout=20)
            cancelled = True
        time.sleep(0.05)
    items = (record or {}).get('items', [])
    return {'operationId': operation, 'state': (record or {}).get('state', 'no_answer'),
            'seconds': round(time.monotonic() - invoked, 2), 'phasesFirstSeenAt': seen,
            'error': ((record or {}).get('error') or {}).get('code', ''),
            'items': [{'bytes': item['artifact'].get('bytes'), 'mime': item['artifact'].get('mime'),
                       'uploadStatus': item.get('uploadStatus'), 'shareStatus': item.get('shareStatus'),
                       'link': bool((item.get('receipt') or {}).get('directUrl')),
                       'error': (item.get('error') or {}).get('code', ''), 'historyId': item['artifact'].get('id')}
                      for item in items],
            '_links': [(item.get('receipt') or {}).get('directUrl', '') for item in items]}


def helpers_gone(within):
    """Seconds until no Proton helper process is left, or None if one outlives `within`."""
    started = time.monotonic()
    while helper_pids():
        if time.monotonic() - started > within:
            return None
        time.sleep(0.1)
    return round(time.monotonic() - started, 2)


def passed(outcome, items=1):
    return (outcome['state'] == 'completed' and len(outcome['items']) == items
            and all(item['uploadStatus'] == 'uploaded' and item['shareStatus'] == 'shared' and item['link']
                    for item in outcome['items']))


def run(app, tests, only):
    results = []

    def record(name, outcome, ok, note=''):
        outcome = {key: value for key, value in outcome.items() if not key.startswith('_')}
        results.append(dict(name=name, passed=bool(ok), note=note, **outcome))
        print(f'{"PASS" if ok else "FAIL"} {name}: {outcome.get("state", "")} in {outcome.get("seconds", "?")} s {note}', flush=True)

    def upload_files(name, paths, items=None):
        invoked = time.monotonic()
        reply, error = app.call('upload.files', {'paths': [str(path) for path in paths], 'profileId': PROFILE_ID})
        if error:
            record(name, {'state': 'refused', 'error': error['code'], 'seconds': 0}, False, error['message'])
            return None
        outcome = follow(app, reply['operationId'], invoked)
        outcome['helperGoneAfter'] = helpers_gone(15)
        record(name, outcome, passed(outcome, items or len(paths)) and outcome['helperGoneAfter'] is not None)
        return outcome

    def capture(name, action, delay=0, cancel_after=None):
        invoked = time.monotonic()
        params = {'action': action, **({'delaySeconds': delay} if delay else {})}
        reply, error = app.call('action.invoke', params, timeout=60)
        if error:
            record(name, {'state': 'refused', 'error': error['code'], 'seconds': 0}, False, error['message'])
            return None
        helper_at = None
        if delay:  # the helper should be starting while the countdown runs
            until = time.monotonic() + min(delay, 2.5)
            while time.monotonic() < until and helper_at is None:
                helper_at = round(time.monotonic() - invoked, 2) if helper_pids() else None
                time.sleep(0.05)
        outcome = follow(app, reply['operationId'], invoked, cancel_after=cancel_after)
        outcome['helperSeenDuringCountdownAt'] = helper_at
        outcome['secondsAfterCountdown'] = round(outcome['seconds'] - delay, 2) if delay else outcome['seconds']
        outcome['helperGoneAfter'] = helpers_gone(40 if cancel_after is not None else 15)
        if cancel_after is not None:
            ok = outcome['state'] == 'cancelled' and outcome['helperGoneAfter'] is not None
            record(name, outcome, ok, 'cancelled during the countdown; the helper must end by itself')
        else:
            record(name, outcome, passed(outcome) and outcome['helperGoneAfter'] is not None,
                   '' if not delay or helper_at is not None else 'no helper was seen during the countdown')
        return outcome

    payloads = app.work / 'payloads'
    payloads.mkdir(exist_ok=True)

    def payload(name, size):
        path = payloads / name
        path.write_bytes(os.urandom(size))
        return path

    wanted = lambda name: not only or name in only
    shared = []
    if wanted('file-64k'):
        outcome = upload_files('file-64k', [payload('acc-64k.bin', 64 * 1024)])
        shared += [(outcome, 0)] if outcome else []
    if wanted('file-1m'):
        outcome = upload_files('file-1m', [payload('acc-1m.bin', 1024 * 1024)])
        shared += [(outcome, 0)] if outcome else []
    if wanted('file-8m'):
        upload_files('file-8m', [payload('acc-8m.bin', 8 * 1024 * 1024)])
    if wanted('batch-3'):
        upload_files('batch-3', [payload(f'acc-batch-{index}.bin', 96 * 1024) for index in range(3)])
    if wanted('text-small'):
        note = payloads / 'acc-note.txt'
        note.write_text('put.gd acceptance synthetic text\n' * 20)
        upload_files('text-small', [note])
    if wanted('back-to-back'):
        first, second = payload('acc-b2b-1.bin', 512 * 1024), payload('acc-b2b-2.bin', 64 * 1024)
        observed = set()
        stop_observer = threading.Event()
        def observe():
            while not stop_observer.is_set():
                for pid in helper_pids():
                    try:
                        ticks = Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1].split()[19]
                        observed.add((pid, ticks))
                    except OSError:
                        pass
                stop_observer.wait(0.01)
        observer = threading.Thread(target=observe, daemon=True)
        observer.start()
        invoked = time.monotonic()
        one, error_one = app.call('upload.files', {'paths': [str(first)], 'profileId': PROFILE_ID})
        two, error_two = app.call('upload.files', {'paths': [str(second)], 'profileId': PROFILE_ID})
        if error_one or error_two:
            record('back-to-back', {'state': 'refused', 'seconds': 0, 'error': (error_one or error_two)['code']}, False)
        else:
            a, b = follow(app, one['operationId'], invoked), follow(app, two['operationId'], invoked)
            merged = {'state': a['state'] if a['state'] == b['state'] else f"{a['state']}+{b['state']}",
                      'seconds': max(a['seconds'], b['seconds']), 'items': a['items'] + b['items'],
                      'firstSeconds': a['seconds'], 'secondSeconds': b['seconds'], 'helperGoneAfter': helpers_gone(15)}
            stop_observer.set()
            observer.join()
            merged['helperProcessesObserved'] = [{'pid': p, 'startTicks': t} for p,t in sorted(observed)]
            merged['helperProcessCount'] = len(observed)
            record('back-to-back', merged, passed(a) and passed(b) and merged['helperGoneAfter'] is not None,
                   'second upload invoked while the first was running')
    for name, action, delay in (('desktop-now', 'desktop', 0), ('desktop-delay3', 'desktop', 3),
                                ('desktop-delay3-again', 'desktop', 3), ('monitor-delay3', 'monitor', 3)):
        if wanted(name):
            outcome = capture(name, action, delay)
            shared += [(outcome, 0)] if outcome else []
    if wanted('cancel-countdown'):
        capture('cancel-countdown', 'desktop', 5, cancel_after=1.5)
        if wanted('after-cancel'):
            upload_files('after-cancel', [payload('acc-after-cancel.bin', 64 * 1024)])
    if wanted('history-picture'):
        # The capture itself is the picture: History is open and shows this run's rows.
        app.call('ui.show', {'view': 'history'}, timeout=30)
        time.sleep(3)
        capture('history-picture', 'desktop', 0)
    # Links: the first good link answers over HTTPS; then every link this run made is revoked.
    if wanted('link-answers'):
        link = next((url for outcome, _ in shared if outcome for url in outcome.get('_links', []) if url), '')
        status, started = 'no link', time.monotonic()
        if link:
            try:
                request = urllib.request.Request(link.split('#')[0], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(request, timeout=30) as answer:
                    status = answer.status
            except Exception as error:  # the status or the kind of failure, never the address
                status = getattr(error, 'code', type(error).__name__)
        record('link-answers', {'state': str(status), 'seconds': round(time.monotonic() - started, 2)}, status == 200,
               'HTTP status of the share page; the address is not recorded')
    if wanted('revoke-all'):
        history = app.need('history.list', {'limit': 100, 'offset': 0})
        rows = history.get('records', [])
        revoked, failed, started = 0, [], time.monotonic()
        timings = []
        for row in rows:
            identity = row.get('id') or row.get('historyId')
            if not row.get('linkAvailable'):
                continue
            one = time.monotonic()
            reply, error = app.call('history.revokeLink', {'id': identity})
            if error:
                if error['code'] not in ('link_unavailable', 'share_not_shared', 'invalid_request'):
                    failed.append(error['code'])
                continue
            deadline, state = time.monotonic() + 120, {}
            while time.monotonic() < deadline:
                state, error = app.call('share.inspect', {'id': reply['shareOperationId']}, timeout=20)
                if error or (state or {}).get('state') != 'running':
                    break
                time.sleep(0.1)
            if (state or {}).get('status') == 'revoked':
                revoked += 1
                timings.append(round(time.monotonic() - one, 2))
            else:
                failed.append((state or {}).get('status') or (error or {}).get('code', 'unknown'))
        gone = helpers_gone(15)
        record('revoke-all', {'state': f'{revoked} revoked', 'seconds': round(time.monotonic() - started, 2),
                              'eachSeconds': timings, 'failures': failed, 'rows': len(rows),
                              'rowKeys': sorted(rows[0].keys()) if rows else [], 'helperGoneAfter': gone},
               revoked > 0 and not failed and gone is not None, 'one helper per History action')
    if not only and app.desktop != 'gnome-shell':
        for index in range(1, 4):
            capture(f'sequential-desktop-{index}', 'desktop')
        for result in run(app, None, {'revoke-all'}):
            result['name'] = 'revoke-additions'
            results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--app', required=True)
    parser.add_argument('--work', required=True)
    parser.add_argument('--host', required=True, help='lock host name: f44, d69, k72, m74 or aurora-amd')
    parser.add_argument('--session', required=True, help='the session id that holds both locks')
    parser.add_argument('--only', nargs='*', default=[])
    args = parser.parse_args()
    require_locks(args.host, args.session)
    work = Path(args.work)
    work.mkdir(mode=0o700)
    if helper_pids():
        raise SystemExit('A Proton helper is already running for this user; another test holds the account')
    app = App(args.app, work)
    report = {'host': os.uname().nodename, 'desktop': app.desktop, 'sessionType': app.environment.get('XDG_SESSION_TYPE'),
              'started': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    try:
        app.authorize_capture()
        app.start()
        report['build'] = json.loads(subprocess.run([str(app.launcher), '--version-json'], env=app.environment,
                                                    capture_output=True, text=True).stdout or '{}')
        report['folder'] = configure(app)
        report['desktopSetup'] = (app.call('desktop.setup')[0] or {}).get('state')
        report['results'] = run(app, None, set(args.only))
        diagnostics, _ = app.call('diagnostics')
        report['providerDiagnostics'] = ((diagnostics or {}).get('providers') or {}).get('proton-drive')
    except Failure as failure:
        report['failure'] = str(failure)
        print('STOPPED:', failure, flush=True)
    finally:
        app.stop()
        app.remove_entries()
        report['helpersLeft'] = helper_pids()
        (work / 'results.json').write_text(json.dumps(report, indent=1) + '\n')
    results = report.get('results', [])
    lines = [f"{report['host']} {report['desktop']} {report.get('sessionType')} build {report.get('build', {}).get('version')}"]
    for item in results:
        sizes = ','.join(str(entry.get('bytes')) for entry in item.get('items', []))
        lines.append(f"{'PASS' if item['passed'] else 'FAIL'}  {item['name']:22s} {str(item.get('state')):12s} "
                     f"{item.get('seconds', '')!s:>7} s  bytes={sizes}  {item.get('note', '')} {item.get('error', '')}")
    lines.append(f"{sum(item['passed'] for item in results)}/{len(results)} passed; helpers left: {report['helpersLeft']}"
                 + (f"; STOPPED: {report['failure']}" if 'failure' in report else ''))
    (work / 'summary.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0 if results and all(item['passed'] for item in results) and 'failure' not in report else 1


if __name__ == '__main__':
    sys.exit(main())
