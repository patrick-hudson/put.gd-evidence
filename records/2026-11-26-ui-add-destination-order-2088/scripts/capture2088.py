#!/usr/bin/env python3
"""Capture before/after pictures of Destinations -> Add destination and Storage service on m74.

Runs a private resident of one build on m74's real Cinnamon/X11 display (:0),
under desktop_lock.py, keeping the window visible on Patrick's wall.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageOps

HOME = Path.home()
UID = os.getuid()
RT = Path(f'/run/user/{UID}/pg2088')
BUS = f'unix:path=/run/user/{UID}/bus'


class Runner:
    def __init__(self, build, run, label):
        self.build = Path(build)
        self.run = Path(run)
        self.label = label
        self.frames = self.run / 'frames'
        for folder in (self.run, self.frames, self.run / 'cfg', self.run / 'data',
                       self.run / 'state', self.run / 'cache', self.run / 'keep'):
            folder.mkdir(parents=True, exist_ok=True)
        os.chmod(self.run, 0o700)
        RT.mkdir(mode=0o700, exist_ok=True)
        sock = str(RT / 'putgd/session.sock')
        assert len(sock.encode('utf-8')) <= 107, f'socket path too long: {sock}'
        self.xenv = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'),
                         DBUS_SESSION_BUS_ADDRESS=BUS)
        self.env = dict(self.xenv, XDG_SESSION_TYPE='x11', XDG_CURRENT_DESKTOP='X-Cinnamon',
                        XDG_CONFIG_HOME=str(self.run / 'cfg'),
                        XDG_DATA_HOME=str(self.run / 'data'),
                        XDG_STATE_HOME=str(self.run / 'state'),
                        XDG_CACHE_HOME=str(self.run / 'cache'),
                        XDG_RUNTIME_DIR=str(RT))
        self.log = open(self.run / 'capture.log', 'a')
        self.facts = {'label': label, 'frames': {}}
        self.resident = None

    def say(self, *parts):
        print(*parts, flush=True)
        print(*parts, file=self.log, flush=True)

    def x(self, *args):
        return subprocess.run(list(args), env=self.xenv, capture_output=True, text=True, timeout=30).stdout.strip()

    def cli(self, method, params=None, timeout=60):
        cmd = [str(self.build / 'putgd-cli'), '--params-stdin', method]
        out = subprocess.run(cmd, env=self.env, input=json.dumps(params or {}),
                             capture_output=True, text=True, timeout=timeout)
        try:
            return json.loads(out.stdout)
        except ValueError:
            return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:300]}, 'result': {}}

    def until(self, check, timeout=20, step=0.25):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            val = check()
            if val:
                return val
            time.sleep(step)
        return None

    def ui_pids(self):
        pids = []
        for pid in subprocess.run(['pgrep', '-u', str(UID), '-x', 'putgd-ui'],
                                  capture_output=True, text=True).stdout.split():
            try:
                if str(RT) in Path(f'/proc/{pid}/environ').read_bytes().decode(errors='replace'):
                    pids.append(int(pid))
            except OSError:
                pass
        return pids

    def geometry(self, window):
        values = dict(line.split('=', 1) for line in self.x('xdotool', 'getwindowgeometry', '--shell', window).splitlines()
                      if '=' in line)
        try:
            return [int(values['X']), int(values['Y']), int(values['WIDTH']), int(values['HEIGHT'])]
        except (KeyError, ValueError):
            return None

    def windows(self):
        ids = set()
        for pid in self.ui_pids():
            ids.update(self.x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split())
        found = []
        for wid in sorted(ids):
            g = self.geometry(wid)
            if g and g[2] > 60 and g[3] > 40:
                found.append((wid, self.x('xdotool', 'getwindowname', wid), g))
        return found

    def main_window(self):
        for wid, name, g in self.windows():
            if name == 'put.gd' and g[2] >= 800:
                return wid, g
        return None, None

    def grab_root(self, path):
        subprocess.run(['import', '-window', 'root', str(path)], env=self.xenv, check=True)
        return path

    def frame(self, name, settle=0.8):
        path = self.frames / f'{self.label}-{name}-full.png'
        time.sleep(settle)
        self.grab_root(path)
        self.facts['frames'][name] = [{'id': w, 'name': n, 'geometry': g} for w, n, g in self.windows()]
        self.say('frame', path.name, self.facts['frames'][name])
        return path

    def ocr_find(self, phrase, region, invert=False):
        """Find exact phrase bounding box [x, y, w, h] in desktop coordinates inside region [rx, ry, rw, rh]."""
        raw = self.run / 'probe-root.png'
        crop_path = self.run / 'probe-crop.png'
        self.grab_root(raw)
        rx, ry, rw, rh = region
        im = Image.open(raw).crop((rx, ry, rx + rw, ry + rh)).convert('L')
        if invert:
            im = ImageOps.invert(im)
        scale = 2
        im = im.resize((im.width * scale, im.height * scale), Image.Resampling.BICUBIC)
        im.save(crop_path)
        tsv = subprocess.run(['tesseract', str(crop_path), 'stdout', '--psm', '11', 'tsv'],
                             capture_output=True, text=True, timeout=30).stdout
        lines = {}
        for row in tsv.splitlines()[1:]:
            parts = row.split('\t')
            if len(parts) < 12:
                continue
            text = parts[11].strip()
            if not text:
                continue
            key = (parts[1], parts[2], parts[3], parts[4])
            lines.setdefault(key, []).append((int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9]), text))
        target = phrase.lower().split()
        for words in lines.values():
            low = [w[4].lower().strip('.,:;…') for w in words]
            for i in range(len(low) - len(target) + 1):
                if low[i:i + len(target)] == target:
                    xs = [words[j][0] for j in range(i, i + len(target))]
                    ys = [words[j][1] for j in range(i, i + len(target))]
                    x2s = [words[j][0] + words[j][2] for j in range(i, i + len(target))]
                    y2s = [words[j][1] + words[j][3] for j in range(i, i + len(target))]
                    x0 = rx + min(xs) // scale
                    y0 = ry + min(ys) // scale
                    w0 = (max(x2s) - min(xs)) // scale
                    h0 = (max(y2s) - min(ys)) // scale
                    return [x0, y0, w0, h0]
        return None

    def find_phrase(self, phrase, region, dark=True):
        # Try inverted first on dark theme (black text on white background works best for tesseract).
        for inv in ((True, False) if dark else (False, True)):
            hit = self.ocr_find(phrase, region, invert=inv)
            if hit:
                return hit
        return None

    def click(self, px, py, settle=0.8):
        self.x('xdotool', 'mousemove', str(px), str(py))
        time.sleep(0.25)
        self.x('xdotool', 'click', '1')
        time.sleep(settle)

    def hover(self, px, py, settle=0.8):
        self.x('xdotool', 'mousemove', str(px), str(py))
        time.sleep(settle)

    def key(self, k, settle=0.4):
        self.x('xdotool', 'key', k)
        time.sleep(settle)

    def start(self):
        ver = json.loads(subprocess.run([str(self.build / 'putgd-cli'), '--version-json'],
                                        capture_output=True, text=True, check=True).stdout)
        self.facts['build'] = ver
        self.say('build', ver.get('version'), ver.get('gitCommit'))
        (RT / 'putgd').mkdir(exist_ok=True)
        (RT / 'putgd/session.sock').unlink(missing_ok=True)
        self.resident = subprocess.Popen([str(self.build / 'putgd'), '--background'],
                                         env=self.env,
                                         stdout=open(self.run / 'resident.log', 'w'),
                                         stderr=subprocess.STDOUT)
        self.facts['residentPid'] = self.resident.pid
        assert self.until(lambda: (RT / 'putgd/session.sock').exists(), 25), 'resident did not start'
        time.sleep(3)
        got = self.cli('settings.get')['result']
        doc = got['document']
        rev = got['metadata']['observedRevision']
        actions = {name: dict(a, shortcut='') for name, a in doc['actions'].items()}
        profile = {
            'id': 'example-s3',
            'label': 'Example S3',
            'provider': 's3',
            'settings': {
                'bucket': 'example-captures',
                'region': 'us-east-1',
                'endpoint': 'https://s3.us-east-1.amazonaws.com',
                'objectPrefix': '',
                'storageClass': 'STANDARD',
                'aclMode': 'omit',
                'linkMode': 'public',
                'linkValidityDays': 7,
                'publicUrlBase': None,
                'addressing': 'auto',
                'connectTimeoutMs': 5000,
                'requestTimeoutMs': 60000,
                'lowSpeedBytesPerSecond': 1,
                'lowSpeedTimeSeconds': 30,
            },
            'credentials': {'mode': 'session', 'reference': None},
        }
        prefs = dict(doc.get('preferences', {}))
        prefs['appearance'] = {'theme': 'dark'}
        if 'updates' in prefs:
            prefs['updates'] = dict(prefs['updates'], check=False)
        patch = {
            'profiles': [profile],
            'actions': actions,
            'archive': dict(doc['archive'], keepUploads=True, root=str(self.run / 'keep')),
            'preferences': prefs,
        }
        patched = self.cli('settings.patch', {'patch': patch, 'expectedRevision': rev})
        self.say('patched', patched['ok'], patched.get('error'))
        assert patched['ok'], patched

    def set_theme(self, theme):
        got = self.cli('settings.get')['result']
        doc = got['document']
        rev = got['metadata']['observedRevision']
        prefs = dict(doc.get('preferences', {}))
        prefs['appearance'] = {'theme': theme}
        patched = self.cli('settings.patch', {'patch': {'preferences': prefs}, 'expectedRevision': rev})
        self.say('theme', theme, patched['ok'])
        assert patched['ok'], patched

    def cleanup(self):
        self.cli('ui.quit')
        time.sleep(1.5)
        if self.resident and self.resident.poll() is None:
            self.resident.terminate()
            try:
                self.resident.wait(8)
            except subprocess.TimeoutExpired:
                self.resident.kill()
        for leftover in (RT / 'putgd/session.sock', RT / 'dconf/user',
                         self.run / 'probe-root.png', self.run / 'probe-crop.png'):
            leftover.unlink(missing_ok=True)
        for folder in (RT / 'putgd', RT / 'dconf', RT):
            try:
                folder.rmdir()
            except OSError:
                pass
        self.say('cleanup done; runtime gone:', not RT.exists())
        (self.run / 'facts.json').write_text(json.dumps(self.facts, indent=2) + '\n')


def center(rect):
    return rect[0] + rect[2] // 2, rect[1] + rect[3] // 2


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--build', required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--label', required=True)
    a = p.parse_args()
    r = Runner(a.build, a.run, a.label)
    try:
        r.x('wmctrl', '-k', 'off')
        r.x('xdotool', 'mousemove', '600', '400')
        time.sleep(0.5)
        r.start()
        shown = r.cli('ui.show', {'view': 'destinations'})
        r.say('ui.show destinations:', shown['ok'])
        wid, geom = r.until(lambda: (lambda pair: pair if pair[0] else None)(r.main_window()), 20)
        assert wid, 'main window did not appear'
        r.x('wmctrl', '-k', 'off')
        r.x('xdotool', 'windowactivate', '--sync', wid)
        r.x('xdotool', 'windowsize', wid, '1160', '780')
        r.x('xdotool', 'windowmove', wid, '120', '60')
        time.sleep(1.2)
        win = r.geometry(wid)
        r.facts['mainWindow'] = win
        r.say('placed:', win)

        # 1. Dark theme: Add destination menu
        add_rect = r.find_phrase('Add destination', win, dark=True)
        assert add_rect, 'Add destination button text not found via OCR'
        r.facts['addButton'] = add_rect
        r.say('addButton:', add_rect)
        r.click(*center(add_rect), settle=1.0)
        r.frame('add-destination-dark')
        r.key('Escape', settle=0.5)

        # 2. Dark theme: Destination actions (⋯) -> Storage service submenu
        # Find "Make default" button text; the 36x36 ⋯ button is immediately to its right.
        default_rect = r.find_phrase('Make default', win, dark=True)
        if default_rect:
            r.facts['makeDefaultButton'] = default_rect
            more_x = default_rect[0] + default_rect[2] + 40
            more_y = default_rect[1] + default_rect[3] // 2
        else:
            title_rect = r.find_phrase('Example S3', [win[0] + 300, win[1], win[2] - 300, 260], dark=True)
            assert title_rect, 'Neither Make default nor Example S3 title found via OCR'
            r.facts['titleRect'] = title_rect
            more_x = win[0] + win[2] - 54
            more_y = title_rect[1] + title_rect[3] // 2
        r.facts['moreButtonClick'] = [more_x, more_y]
        r.say('moreButtonClick:', [more_x, more_y])
        r.click(more_x, more_y, settle=0.8)
        svc_rect = r.find_phrase('Storage service', win, dark=True)
        assert svc_rect, 'Storage service menu item not found via OCR'
        r.facts['storageServiceItem'] = svc_rect
        r.say('storageServiceItem:', svc_rect)
        r.hover(*center(svc_rect), settle=1.0)
        r.frame('storage-service-dark')
        r.key('Escape', settle=0.4)
        r.key('Escape', settle=0.5)

        # 3. Light theme: Add destination menu
        r.set_theme('light')
        time.sleep(1.2)
        add_light = r.find_phrase('Add destination', win, dark=False)
        assert add_light, 'Add destination button text not found in light theme'
        r.facts['addButtonLight'] = add_light
        r.click(*center(add_light), settle=1.0)
        r.frame('add-destination-light')
        r.key('Escape', settle=0.5)
    finally:
        r.cleanup()


if __name__ == '__main__':
    main()
