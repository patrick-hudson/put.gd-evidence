"""Shared helpers for the #2042 Settings pictures: a PRIVATE resident of the build under test on m74's real
Cinnamon/X11 display, driven with putgd-cli, and ImageMagick `import` frames of the whole desktop.
Run only with the desktop lock held (desktop_lock.py run m74 ...)."""
import json
import os
import subprocess
import time
from pathlib import Path

HOME = Path.home()
UID = os.getuid()
RT = Path('/run/user/%d/pg2042' % UID)
BUS = 'unix:path=/run/user/%d/bus' % UID


class Run:
    def __init__(self, build, run, label):
        self.build, self.run, self.label = Path(build), Path(run), label
        self.frames = self.run / 'frames'
        for folder in (self.run, self.frames, self.run / 'cfg', self.run / 'data', self.run / 'state', self.run / 'cache', self.run / 'keep'):
            folder.mkdir(parents=True, exist_ok=True)
        os.chmod(self.run, 0o700)
        RT.mkdir(mode=0o700, exist_ok=True)
        sock = str(RT / 'putgd/session.sock')
        assert len(sock.encode()) <= 107, sock
        self.xenv = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS)
        self.env = dict(self.xenv, XDG_SESSION_TYPE='x11', XDG_CURRENT_DESKTOP='X-Cinnamon', XDG_CONFIG_HOME=str(self.run / 'cfg'),
                        XDG_DATA_HOME=str(self.run / 'data'), XDG_STATE_HOME=str(self.run / 'state'), XDG_CACHE_HOME=str(self.run / 'cache'), XDG_RUNTIME_DIR=str(RT))
        self.log = open(self.run / 'capture.log', 'a')
        self.facts = {'label': label, 'frames': {}}
        self.resident = None

    def say(self, *parts):
        print(*parts, flush=True)
        print(*parts, file=self.log, flush=True)

    def cli(self, method, params=None, timeout=120):
        out = subprocess.run([str(self.build / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}), capture_output=True, text=True, env=self.env, timeout=timeout)
        try:
            return json.loads(out.stdout)
        except ValueError:
            return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:300]}, 'result': {}}

    def x(self, *args):
        return subprocess.run(list(args), capture_output=True, text=True, env=self.xenv).stdout.strip()

    def until(self, check, seconds=30, step=0.3):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            value = check()
            if value:
                return value
            time.sleep(step)
        return None

    def ui_pids(self):
        pids = []
        for comm in ('putgd-ui', 'putgd-record'):
            for pid in subprocess.run(['pgrep', '-u', str(UID), '-x', comm], capture_output=True, text=True).stdout.split():
                try:
                    if str(RT) in Path('/proc/%s/environ' % pid).read_bytes().decode(errors='replace'):
                        pids.append(int(pid))
                except OSError:
                    pass
        return pids

    def geometry(self, window):
        values = dict(line.split('=') for line in self.x('xdotool', 'getwindowgeometry', '--shell', window).splitlines() if '=' in line)
        try:
            return [int(values['X']), int(values['Y']), int(values['WIDTH']), int(values['HEIGHT'])]
        except (KeyError, ValueError):
            return None

    def windows(self):
        ids = set()
        for pid in self.ui_pids():
            ids.update(self.x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split())
        found = []
        for window in sorted(ids):
            g = self.geometry(window)
            if g and g[2] > 60 and g[3] > 30:
                found.append((window, self.x('xdotool', 'getwindowname', window), g))
        return found

    def frame(self, name, settle=0.6):
        path = self.frames / ('%s-%s-full.png' % (self.label, name))
        time.sleep(settle)
        subprocess.run(['import', '-window', 'root', str(path)], env=self.xenv)
        self.facts['frames'][name] = [{'id': w, 'name': n, 'geometry': g} for w, n, g in self.windows()]
        self.say('frame', path.name, self.facts['frames'][name])
        return path

    def park(self):
        self.x('xdotool', 'mousemove', '1900', '500')

    def place(self, window, left, top, width, height):
        self.x('xdotool', 'windowactivate', window)
        self.x('xdotool', 'windowsize', window, str(width), str(height))
        self.x('xdotool', 'windowmove', window, str(left), str(top))
        time.sleep(1.0)

    def click(self, px, py, settle=0.8):
        self.x('xdotool', 'mousemove', str(px), str(py))
        time.sleep(0.25)
        self.x('xdotool', 'click', '1')
        time.sleep(settle)

    def hover(self, px, py, wait=2.2):
        # A tooltip needs the pointer to arrive and then rest over the control.
        self.x('xdotool', 'mousemove', str(px - 6), str(py - 2))
        time.sleep(0.3)
        self.x('xdotool', 'mousemove', str(px), str(py))
        time.sleep(wait)

    def start(self, check_updates_off=True):
        version = json.loads(subprocess.run([str(self.build / 'putgd-cli'), '--version-json'], capture_output=True, text=True).stdout)
        self.facts['build'] = version
        self.say('build', version.get('version'), version.get('gitCommit'))
        (RT / 'putgd').mkdir(exist_ok=True)
        (RT / 'putgd/session.sock').unlink(missing_ok=True)
        self.resident = subprocess.Popen([str(self.build / 'putgd'), '--background'], env=self.env, stdout=open(self.run / 'resident.log', 'w'), stderr=subprocess.STDOUT)
        self.facts['residentPid'] = self.resident.pid
        assert self.until(lambda: (RT / 'putgd/session.sock').exists(), 20), 'resident did not start'
        time.sleep(5)
        document = self.cli('settings.get')['result']['document']
        actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}
        patch = {'actions': actions, 'archive': dict(document['archive'], keepUploads=True, root=str(self.run / 'keep'))}
        if check_updates_off and 'updates' in document.get('preferences', {}):
            patch['preferences'] = {'updates': dict(document['preferences']['updates'], check=False)}
        revision = self.cli('settings.get')['result']['metadata']['observedRevision']
        patched = self.cli('settings.patch', {'patch': patch, 'expectedRevision': revision})
        self.say('patched', patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))

    def cleanup(self):
        self.cli('ui.quit')
        time.sleep(1.5)
        if self.resident and self.resident.poll() is None:
            self.resident.terminate()
            try:
                self.resident.wait(8)
            except subprocess.TimeoutExpired:
                self.resident.kill()
        for leftover in (RT / 'putgd/session.sock', RT / 'dconf/user'):
            leftover.unlink(missing_ok=True)
        for folder in (RT / 'putgd', RT / 'dconf', RT / 'pulse', RT):
            try:
                folder.rmdir()
            except OSError:
                pass
        self.say('cleanup done; runtime folder gone:', not RT.exists())
        (self.run / 'facts.json').write_text(json.dumps(self.facts, indent=1))
