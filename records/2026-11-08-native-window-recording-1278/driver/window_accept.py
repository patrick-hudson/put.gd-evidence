#!/usr/bin/env python3
"""#1278 acceptance driver: window recording on KDE/GNOME Wayland without the
portal chooser. Run on the host from a plain SSH shell while holding the
desktop's lock. Uses a private put.gd profile under --run and test windows it
starts itself; prints one JSON summary and writes results.json.

  window_accept.py --run DIR --bin DIR --repo DIR [--kwin-entry] [--input-socket PATH]

--bin holds putgd, putgd-cli and putgd-record (a build tree or /usr/bin).
--repo is a put.gd checkout (for tools/lab/record_run.py's session environment).
--kwin-entry writes a temporary putgd-record desktop entry for a scratch build.
"""
import argparse, json, os, re, shutil, signal, socket, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def log(message):
    print(time.strftime('%H:%M:%S ') + message, file=sys.stderr, flush=True)


class Fail(RuntimeError):
    pass


class Window:
    """A test window driven over stdin."""
    def __init__(self, driver, title, still=False, size='640x480', color=None):
        self.title = title
        command = [sys.executable, str(HERE / 'win1278.py'), '--title', title, '--size', size]
        if still:
            command.append('--still')
        if color:
            command += ['--color', color]
        self.process = subprocess.Popen(command, env=driver.session, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=open(driver.run / 'logs' / ('window-%s.log' % title.replace(' ', '-')), 'a'), text=True)
        line = self.process.stdout.readline().strip()
        if line != 'mapped':
            raise Fail('test window %s did not map: %r' % (title, line))
        self.identity = None

    def send(self, command):
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()
        return self.process.stdout.readline().strip()

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(5)
            except subprocess.TimeoutExpired:
                self.process.kill()


class Driver:
    def __init__(self, args):
        self.args = args
        self.run = Path(args.run).resolve()
        for name in ('config', 'data', 'cache', 'state', 'working', 'out', 'frames', 'logs', 'archive'):
            (self.run / name).mkdir(parents=True, exist_ok=True)
        os.chmod(self.run, 0o700)
        sys.path.insert(0, str(Path(args.repo) / 'tools/lab'))
        from record_run import session_environment
        self.session, self.desktop = session_environment()
        self.session.setdefault('PIPEWIRE_RUNTIME_DIR', self.session.get('XDG_RUNTIME_DIR', '/run/user/%d' % os.getuid()))
        self.env = dict(self.session, XDG_CONFIG_HOME=str(self.run / 'config'), XDG_DATA_HOME=str(self.run / 'data'),
                        XDG_CACHE_HOME=str(self.run / 'cache'), XDG_STATE_HOME=str(self.run / 'state'),
                        PUTGD_RECORD_KEEP_WORKING=str(self.run / 'working'), PUTGD_RECORD_DEBUG_LOG=str(self.run / 'logs/record-debug.log'))
        self.bin = Path(args.bin).resolve() if args.bin else None
        self.launcher = [str(self.bin / 'putgd'), '--background'] if self.bin else None
        self.helper_env = self.env
        self.real_data = None
        if args.appimage:
            # The AppImage's KWin permission entries only work in the user's own data
            # directory, so put.gd's data goes there and is moved into the run afterwards.
            appimage = Path(args.appimage).resolve()
            appdir = self.run / 'appdir'
            if not (appdir / 'squashfs-root').is_dir():
                appdir.mkdir(exist_ok=True)
                subprocess.run([str(appimage), '--appimage-extract'], cwd=appdir, check=True, stdout=subprocess.DEVNULL)
            self.bin = appdir / 'squashfs-root/usr/bin'
            self.launcher = [str(appimage), '--background']
            self.helper_env = dict(self.env, APPDIR=str(appdir / 'squashfs-root'))
            self.real_data = Path(os.environ['HOME']) / '.local/share/putgd'
            if self.real_data.exists():
                raise Fail('%s exists; the AppImage run would mix with it' % self.real_data)
            del self.env['XDG_DATA_HOME']
        self.socket = Path(self.session['XDG_RUNTIME_DIR']) / 'putgd' / 'session.sock'
        self.kde = 'kde' in self.session.get('XDG_CURRENT_DESKTOP', '').lower()
        self.entry = None
        self.resident = None
        self.windows = []
        self.results = {'host': socket.gethostname(), 'desktop': self.session.get('XDG_CURRENT_DESKTOP'), 'cases': {}}

    # -- put.gd ---------------------------------------------------------------
    def cli(self, method, params=None, timeout=60, allow_error=False):
        result = subprocess.run([str(self.bin / 'putgd-cli'), method, json.dumps(params or {})], env=self.env,
                                capture_output=True, text=True, timeout=timeout)
        try:
            reply = json.loads(result.stdout)
        except ValueError:
            raise Fail('%s: no JSON reply (exit %d): %s' % (method, result.returncode, result.stderr.strip()[-300:]))
        if not reply.get('ok') and not allow_error:
            error = reply.get('error') or {}
            raise Fail('%s failed: %s %s' % (method, error.get('code'), error.get('message')))
        return reply if allow_error else (reply.get('result') or {})

    def start_resident(self):
        if self.socket.exists():
            raise Fail('%s exists: another put.gd resident owns this session' % self.socket)
        self.resident = subprocess.Popen(self.launcher, env=self.env, stdin=subprocess.DEVNULL,
                                         stdout=open(self.run / 'logs/resident.log', 'a'), stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                caps = self.cli('recording.capabilities', timeout=40)
                break
            except (Fail, subprocess.TimeoutExpired):
                time.sleep(0.5)
        else:
            raise Fail('resident did not answer')
        settings = self.cli('settings.get')
        root = str(self.run / 'archive')
        self.cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': root}},
                                    'expectedRevision': (settings.get('metadata') or {}).get('observedRevision')})
        return caps

    def stop_resident(self):
        if self.resident is None:
            return
        try:
            self.cli('ui.quit', timeout=15)
        except (Fail, subprocess.TimeoutExpired):
            pass
        try:
            self.resident.wait(20)
        except subprocess.TimeoutExpired:
            os.killpg(self.resident.pid, signal.SIGTERM)
            self.resident.wait(10)
        self.resident = None

    def inspect(self, rid):
        return self.cli('recording.inspect', {'id': rid})

    def wait(self, rid, states, timeout):
        started = time.monotonic()
        while time.monotonic() - started < timeout:
            reply = self.cli('recording.inspect', {'id': rid}, allow_error=True)
            if not reply.get('ok'):
                outcome = self.cli('operation.inspect', {'id': rid}, allow_error=True)
                raise Fail('session ended: %s' % json.dumps((outcome.get('result') or {}).get('error') or reply.get('error')))
            info = reply['result']
            if info.get('state') in states:
                return info, round(time.monotonic() - started, 3)
            time.sleep(0.1)
        raise Fail('timed out waiting for %s (a picker on screen would hold prepare here)' % '/'.join(states))

    def motion(self, clip):
        result = subprocess.run([str(self.bin / 'putgd-record'), '--motion', str(clip), '12'], env=self.helper_env, capture_output=True, text=True, timeout=300)
        found = re.search(r'^motion=([0-9.]+)', result.stdout, re.M)
        return float(found.group(1)) if found else 'error: ' + (result.stdout + result.stderr).strip()[-200:]

    def frames(self, clip, name, duration_us, count=6):
        kept = []
        for i in range(count):
            at = int(duration_us * (i + 0.5) / count)
            out = self.run / 'frames' / ('%s-%02d.png' % (name, i))
            result = subprocess.run([str(self.bin / 'putgd-record'), '--preview', str(clip), str(at), str(out)], env=self.helper_env, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                kept.append(out.name)
        return kept

    # -- the desktop ----------------------------------------------------------
    def kwin_script(self, body, name):
        path = self.run / ('%s.js' % name)
        path.write_text(body)
        dbus = lambda *a: subprocess.run(['dbus-send', '--session', '--print-reply=literal', '--dest=org.kde.KWin', *a], env=self.session, capture_output=True, text=True, timeout=10)
        loaded = dbus('/Scripting', 'org.kde.kwin.Scripting.loadScript', 'string:%s' % path, 'string:%s' % name)
        script = loaded.stdout.split()[-1] if loaded.stdout.split() else ''
        dbus('/Scripting/Script%s' % script, 'org.kde.kwin.Script.run')
        time.sleep(0.4)
        dbus('/Scripting', 'org.kde.kwin.Scripting.unloadScript', 'string:%s' % name)

    def kwin_window(self, window, body, label):
        self.kwin_script('for (const w of workspace.windowList()) if (w.internalId.toString() === %s) { %s }\n' % (json.dumps(window.identity), body), 'putgd1278-' + label)
        log('%s %s' % (label, window.title))

    def key(self, *keys):
        """Press keys together through the lab input agent (QMP)."""
        if not self.args.input_socket:
            raise Fail('no input agent')
        with socket.socket(socket.AF_UNIX) as s:
            s.connect(self.args.input_socket)
            f = s.makefile('rw')
            f.readline()
            def send(obj):
                f.write(json.dumps(obj) + '\n'); f.flush()
                return f.readline()
            send({'execute': 'qmp_capabilities'})
            down = [{'type': 'key', 'data': {'down': True, 'key': {'type': 'qcode', 'data': k}}} for k in keys]
            up = [{'type': 'key', 'data': {'down': False, 'key': {'type': 'qcode', 'data': k}}} for k in reversed(keys)]
            send({'execute': 'input-send-event', 'arguments': {'events': down}})
            time.sleep(0.1)
            send({'execute': 'input-send-event', 'arguments': {'events': up}})

    def pointer_sweep(self, rect, screen):
        """Move the pointer across the window (absolute, over the whole screen)."""
        if not self.args.input_socket:
            return False
        with socket.socket(socket.AF_UNIX) as s:
            s.connect(self.args.input_socket)
            f = s.makefile('rw')
            f.readline()
            def send(obj):
                f.write(json.dumps(obj) + '\n'); f.flush()
                return f.readline()
            send({'execute': 'qmp_capabilities'})
            for i in range(20):
                x = rect[0] + rect[2] * (0.2 + 0.6 * i / 19)
                y = rect[1] + rect[3] * 0.5
                send({'execute': 'input-send-event', 'arguments': {'events': [
                    {'type': 'abs', 'data': {'axis': 'x', 'value': int(x / screen[0] * 32767)}},
                    {'type': 'abs', 'data': {'axis': 'y', 'value': int(y / screen[1] * 32767)}}]}})
                time.sleep(0.05)
        return True

    def kwin_entry(self):
        directory = Path(os.environ['HOME']) / '.local/share/applications'
        directory.mkdir(parents=True, exist_ok=True)
        self.entry = directory / 'putgd-record-1278-lab.desktop'
        self.entry.write_text('[Desktop Entry]\nType=Application\nName=put.gd screen recorder (#1278 lab)\nExec=%s\nNoDisplay=true\n'
                              'StartupWMClass=putgd-record\nX-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1\n' % (self.bin / 'putgd-record').resolve())
        subprocess.run(['kbuildsycoca6', '--noincremental'], env=self.session, capture_output=True, timeout=120)
        log('wrote %s' % self.entry)

    def open_window(self, title, **kwargs):
        window = Window(self, title, **kwargs)
        self.windows.append(window)
        time.sleep(1.0)
        return window

    def identify(self, window):
        listed = self.cli('recording.windows')
        for entry in listed.get('windows', []):
            if entry.get('title') == window.title:
                window.identity = entry['identity']
                return entry
        raise Fail('%s is not in recording.windows: %s' % (window.title, json.dumps(listed)[:400]))

    # -- cases ----------------------------------------------------------------
    def record(self, name, target, during, settle=1.0, expect_stop=None):
        """prepare → ready (timed, no dialog) → start → `during()` → stop or expected self-stop → saveCopy → measure."""
        case = {'target': target}
        prepared = self.cli('recording.prepare', {'target': target, 'format': 'mp4', 'fps': 30})
        rid = prepared['recordingId']
        ready, case['prepareS'] = self.wait(rid, ('ready',), 20)
        case.update(canvas=ready.get('canvas'), window=ready.get('window'), resolvedTarget=ready.get('target'), overlay=ready.get('overlayPlacement'))
        time.sleep(settle)
        self.cli('recording.start', {'id': rid})
        case['events'] = during(rid) or []
        if expect_stop:
            info, case['selfStopS'] = self.wait(rid, ('reviewing',), 15)
            case['stopReason'] = info.get('stopReason')
        else:
            info = self.cli('recording.stop', {'id': rid}, timeout=60)
        case['durationUs'] = info.get('durationUs')
        copy = self.run / 'out' / ('%s.mp4' % name)
        self.cli('recording.saveCopy', {'id': rid, 'path': str(copy), 'overwrite': True})
        done, _ = self.wait(rid, ('reviewing',), 300)
        case['export'] = (done.get('lastExport') or {}).get('status')
        self.cli('recording.cancel', {'id': rid})
        if copy.is_file():
            case.update(bytes=copy.stat().st_size, motion=self.motion(copy), frames=self.frames(copy, name, case['durationUs'] or 1000000))
        working = self.run / 'working' / (rid + '.mkv')
        if working.is_file():
            case['workingMotion'] = self.motion(working)
        self.results['cases'][name] = case
        log('%s: %s' % (name, json.dumps({k: case.get(k) for k in ('prepareS', 'canvas', 'durationUs', 'motion', 'stopReason', 'selfStopS')})))
        return case

    def gate(self):
        """The GNOME extension gate: what the loaded extension says and what a window recording gets."""
        try:
            self.start_resident()
            caps = self.cli('capabilities')
            helper = caps.get('helper') or (caps.get('source') or {}).get('helper') or {}
            self.results['helper'] = {k: helper.get(k) for k in ('available', 'extensionVersion', 'packagedExtensionVersion', 'outdated', 'recordingVersion')}
            listed = self.cli('recording.windows', allow_error=True)
            self.results['windows'] = listed.get('error') or {'ok': True, 'count': len((listed.get('result') or {}).get('windows', []))}
            prepared = self.cli('recording.prepare', {'target': {'kind': 'window'}, 'format': 'mp4'}, allow_error=True)
            rid = (prepared.get('result') or {}).get('recordingId')
            if rid:
                try:
                    info, _ = self.wait(rid, ('ready',), 15)
                    self.results['prepare'] = {'state': info.get('state')}
                    self.cli('recording.cancel', {'id': rid})
                except Fail as error:
                    self.results['prepare'] = {'ended': str(error)}
            else:
                self.results['prepare'] = prepared.get('error')
        except Exception as error:
            self.results['error'] = '%s: %s' % (type(error).__name__, error)
        finally:
            self.stop_resident()
            (self.run / 'gate.json').write_text(json.dumps(self.results, indent=1))
            print(json.dumps(self.results, indent=1))

    def click(self, x, y, screen):
        with socket.socket(socket.AF_UNIX) as s:
            s.connect(self.args.input_socket)
            f = s.makefile('rw')
            f.readline()
            def send(obj):
                f.write(json.dumps(obj) + '\n'); f.flush()
                return f.readline()
            send({'execute': 'qmp_capabilities'})
            send({'execute': 'input-send-event', 'arguments': {'events': [
                {'type': 'abs', 'data': {'axis': 'x', 'value': int(x / screen[0] * 32767)}},
                {'type': 'abs', 'data': {'axis': 'y', 'value': int(y / screen[1] * 32767)}}]}})
            time.sleep(0.2)
            for down in (True, False):
                send({'execute': 'input-send-event', 'arguments': {'events': [{'type': 'btn', 'data': {'down': down, 'button': 'left'}}]}})
                time.sleep(0.1)

    def short(self):
        """Focus a moving window by clicking it, then the active-window, monitor and region cases."""
        try:
            # The resident first: a first run opens its dashboard, which must not end up above the window.
            self.start_resident()
            time.sleep(3)
            moving = self.open_window('putgd-1278 motion', size='900x700')
            entry = self.identify(moving)
            rect = entry['rect']
            self.click(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2, self.args.screen)
            time.sleep(1)
            listed = self.cli('recording.windows')
            active = next((w for w in listed.get('windows', []) if w.get('active')), None)
            self.results['activeBefore'] = active and {k: active.get(k) for k in ('identity', 'title')}
            self.results['activeExcluded'] = listed.get('activeExcluded')
            case = self.record('active-window', {'kind': 'window'}, lambda rid: time.sleep(3))
            case['matchesActive'] = bool(active) and (case.get('resolvedTarget') or {}).get('identity') == active['identity'] == moving.identity
            self.record('monitor', {'kind': 'monitor'}, lambda rid: time.sleep(3))
            self.record('region', {'kind': 'region', 'rect': [rect[0], rect[1], 800, 600]}, lambda rid: time.sleep(3))
        except Exception as error:
            self.results['error'] = '%s: %s' % (type(error).__name__, error)
            log('FAILED: %s' % self.results['error'])
        finally:
            self.stop_resident()
            for window in self.windows:
                window.close()
            (self.run / 'results.json').write_text(json.dumps(self.results, indent=1))
            print(json.dumps(self.results, indent=1))

    def main(self):
        a = self.args
        if a.gate_only:
            return self.gate()
        if a.short:
            return self.short()
        try:
            if a.kwin_entry:
                self.kwin_entry()
            moving = self.open_window('putgd-1278 motion')
            still = self.open_window('putgd-1278 still', still=True, color='0.25,0.05,0.05')
            caps = self.start_resident()
            self.results['capabilities'] = {k: caps.get(k) for k in ('available', 'acquisition', 'windowAcquisition', 'targets', 'windowList', 'kdeScreencast', 'mutterScreenCast', 'portal')}
            log('capabilities: %s' % json.dumps(self.results['capabilities']))
            listed = self.cli('recording.windows')
            self.results['windowsListed'] = [{k: w.get(k) for k in ('identity', 'title', 'appId', 'active', 'minimized')} for w in listed.get('windows', [])]
            self.results['activeExcluded'] = listed.get('activeExcluded')
            self.identify(moving)
            self.identify(still)

            # 1. Motion while the window moves, resizes, is covered and minimized.
            def churn(rid):
                events = []
                mark = lambda what: events.append([what, round(time.monotonic() - started, 2)])
                started = time.monotonic()
                time.sleep(2)
                if self.kde:
                    self.kwin_window(moving, 'w.frameGeometry = {x: 420, y: 260, width: w.frameGeometry.width, height: w.frameGeometry.height};', 'move'); mark('moved')
                    time.sleep(2)
                    self.kwin_window(moving, 'w.frameGeometry = {x: 120, y: 90, width: 1000, height: 700};', 'resize'); mark('resized')
                else:
                    moving.send('maximize'); mark('maximized (moved and resized)')
                    time.sleep(2)
                    moving.send('unmaximize'); mark('unmaximized')
                    time.sleep(1)
                    moving.send('resize 1000 700'); mark('resized by the app')
                    if a.input_socket:
                        time.sleep(1)
                        self.key('meta_l', 'left'); mark('Super+Left (tiled left: moved and resized)')
                time.sleep(2)
                screen = a.screen
                rect = self.cli('recording.windows')
                rect = next((w['rect'] for w in rect.get('windows', []) if w['identity'] == moving.identity), None)
                if rect and self.pointer_sweep(rect, screen):
                    mark('pointer swept across the window')
                if self.kde:
                    self.kwin_window(still, 'w.frameGeometry = {x: 0, y: 0, width: 1400, height: 900}; workspace.activeWindow = w;', 'cover'); mark('covered by another window')
                else:
                    still.send('maximize'); still.send('present'); mark('covered (other window maximized and presented)')
                time.sleep(2)
                if self.kde:
                    self.kwin_window(moving, 'w.minimized = true;', 'minimize'); mark('minimized')
                    time.sleep(2)
                    self.kwin_window(moving, 'w.minimized = false; workspace.activeWindow = w;', 'restore'); mark('restored')
                else:
                    moving.send('iconify'); mark('minimized')
                    time.sleep(2)
                    mark('(GNOME: a client cannot unminimize itself; left minimized)')
                time.sleep(2)
                return events
            self.record('churn', {'kind': 'window', 'identity': moving.identity}, churn)
            if self.kde:
                self.kwin_window(still, 'w.frameGeometry = {x: 900, y: 120, width: 640, height: 480};', 'uncover')
                self.kwin_window(moving, 'w.minimized = false;', 'restore')
            else:
                still.send('unmaximize')

            # 2. Static control on the same desktop.
            self.record('still-control', {'kind': 'window', 'identity': still.identity}, lambda rid: time.sleep(4))

            # 3. The window closes while recording: a clean end into review.
            closing = self.open_window('putgd-1278 closing', color='0.05,0.25,0.10')
            self.identify(closing)
            def close_it(rid):
                time.sleep(3)
                at = time.monotonic()
                closing.close()
                return [['window closed', 3.0]]
            self.record('target-closed', {'kind': 'window', 'identity': closing.identity}, close_it, expect_stop=True)

            # 4. No identity: the active external window.
            active = next((w for w in self.cli('recording.windows').get('windows', []) if w.get('active')), None)
            self.results['activeBefore'] = active and {k: active.get(k) for k in ('identity', 'title')}
            if active:
                case = self.record('active-window', {'kind': 'window'}, lambda rid: time.sleep(2))
                case['matchesActive'] = (case.get('resolvedTarget') or {}).get('identity') == active['identity']

            # 5. No regressions: a monitor and a region with the moving window in it.
            self.record('monitor', {'kind': 'monitor'}, lambda rid: time.sleep(3))
            self.record('region', {'kind': 'region', 'rect': [100, 80, 800, 600]}, lambda rid: time.sleep(3))
        except Exception as error:
            self.results['error'] = '%s: %s' % (type(error).__name__, error)
            log('FAILED: %s' % self.results['error'])
        finally:
            self.stop_resident()
            for window in self.windows:
                window.close()
            if self.entry:
                self.entry.unlink(missing_ok=True)
                subprocess.run(['kbuildsycoca6', '--noincremental'], env=self.session, capture_output=True, timeout=120)
                log('removed %s' % self.entry)
            if self.real_data and self.real_data.exists():
                shutil.move(str(self.real_data), str(self.run / 'data-moved'))
                log('moved %s into the run' % self.real_data)
            (self.run / 'results.json').write_text(json.dumps(self.results, indent=1))
            print(json.dumps(self.results, indent=1))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--run', required=True)
    p.add_argument('--bin')
    p.add_argument('--appimage')
    p.add_argument('--repo', required=True)
    p.add_argument('--kwin-entry', action='store_true')
    p.add_argument('--gate-only', action='store_true')
    p.add_argument('--short', action='store_true')
    p.add_argument('--input-socket')
    p.add_argument('--screen', type=lambda s: [int(v) for v in s.split('x')], default=[1920, 1080])
    Driver(p.parse_args()).main()
